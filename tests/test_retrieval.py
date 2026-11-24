"""Retrieval pre-filter, naive leak, and extractive answers."""

from __future__ import annotations

import unittest

from securerag.acl import user_can_read
from securerag.engine import SecureRagEngine
from securerag.index import build_index
from securerag.samples import SAMPLES
from securerag.users import all_users, get_user

# Figures that must never appear for a service advisor in secure mode.
RESTRICTED_MARKERS = (
    "$185,000",
    "$241,000",
    "$265,000",
    "$344,500",
    "$310,000",
    "$18.5 million",
    "on-target earnings are $241,000",
)
HONDA_PL_MARKERS = (
    "$186,400",
    "$4,820,000",
)
PATEL_MARKERS = (
    "$1,140",
    "$2,410",
    "T-4821",
)


def _engine() -> SecureRagEngine:
    # Fresh engine + audit per test class setup, shared index is cheap.
    return SecureRagEngine(index=build_index())


class PrefilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = _engine()

    def test_secure_candidates_are_only_authorized_chunks(self):
        for user in all_users():
            eligible = self.engine.index.eligible_chunks(user, naive=False)
            self.assertTrue(eligible, f"{user.id} should still see some docs")
            for chunk in eligible:
                self.assertTrue(
                    user_can_read(user, chunk),
                    f"{user.id} was offered unauthorized chunk {chunk.id}",
                )
            # And nothing authorized was dropped.
            authorized = [c for c in self.engine.index.chunks if user_can_read(user, c)]
            self.assertEqual({c.id for c in eligible}, {c.id for c in authorized})

    def test_no_unauthorized_chunk_ever_in_secure_context(self):
        questions = [s["question"] for s in SAMPLES] + [
            "What is Patricia Walsh's base salary and on-target earnings?",
            "How much did the group make in October?",
            "Tell me about the Patel deal reserve and backend gross.",
        ]
        for user in all_users():
            for question in questions:
                result = self.engine.ask(user, question, naive=False, use_llm=False, record=True)
                for item in result.retrieval.chunks:
                    self.assertTrue(
                        item.allowed,
                        f"{user.id} received unauthorized {item.chunk.id} for {question!r}",
                    )
                    self.assertTrue(user_can_read(user, item.chunk))
                self.assertEqual(result.retrieval.leaked_chunks, [])
                self.assertEqual(result.retrieval.mode, "secure")
                # Pre-filter: every candidate scored was authorized, not just the top-k.
                for chunk_id in result.retrieval.candidate_ids:
                    chunk = self.engine.index.get_chunk(chunk_id)
                    self.assertIsNotNone(chunk)
                    self.assertTrue(user_can_read(user, chunk), chunk_id)

    def test_secure_search_scores_only_eligible_rows(self):
        maya = get_user("maya")
        eligible = self.engine.index.eligible_indices(maya, naive=False)
        result = self.engine.index.search("pay plan", maya, naive=False)
        self.assertEqual(result.candidates_considered, int(eligible.size))
        self.assertLess(result.candidates_considered, len(self.engine.index.chunks))
        self.assertGreater(result.filtered_out_count, 0)
        self.assertGreater(result.filtered_out_by_sensitivity.get("restricted", 0), 0)


class NaiveLeakTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = _engine()

    def test_naive_mode_leaks_honda_pay_plan_to_service_advisor(self):
        result = self.engine.ask(
            "maya",
            "What is the general manager pay plan at Lakeside Honda?",
            naive=True,
            use_llm=False,
        )
        self.assertEqual(result.retrieval.mode, "naive")
        self.assertEqual(result.retrieval.filtered_out_count, 0)
        leaked_ids = {item.chunk.doc_id for item in result.retrieval.leaked_chunks}
        self.assertIn("hr-pay-plan-gm-honda", leaked_ids)
        blob = result.answer.text + " " + " ".join(item.chunk.text for item in result.retrieval.chunks)
        self.assertTrue(
            any(marker in blob for marker in ("$185,000", "$241,000", "Patricia Walsh")),
            blob,
        )

    def test_secure_mode_does_not_leak_pay_plan_or_profit_to_maya(self):
        for question, markers in (
            ("What is the general manager pay plan at Lakeside Honda?", RESTRICTED_MARKERS),
            ("What was Lakeside Honda's net profit in October?", HONDA_PL_MARKERS),
            ("What F&I products were sold on the Patel deal at Toyota, and what was the reserve?", PATEL_MARKERS),
        ):
            result = self.engine.ask("maya", question, naive=False, use_llm=False)
            context = " ".join(item.chunk.text for item in result.retrieval.chunks)
            combined = result.answer.text + " " + context
            for marker in markers:
                self.assertNotIn(marker, combined, f"{question} leaked {marker}")
            doc_ids = {item.chunk.doc_id for item in result.retrieval.chunks}
            self.assertNotIn("hr-pay-plan-gm-honda", doc_ids)
            self.assertNotIn("pl-honda-2026-10", doc_ids)
            self.assertNotIn("fi-deal-toyota-patel", doc_ids)

    def test_cfo_secure_mode_can_see_pay_plan_and_profit(self):
        pay = self.engine.ask(
            "jonathan",
            "What is the general manager pay plan at Lakeside Honda?",
            naive=False,
            use_llm=False,
        )
        self.assertFalse(pay.answer.refusal)
        blob = pay.answer.text + " " + " ".join(c.chunk.text for c in pay.retrieval.chunks)
        self.assertIn("$185,000", blob)
        self.assertIn("Patricia Walsh", blob)

        profit = self.engine.ask(
            "jonathan",
            "What was Lakeside Honda's net profit in October?",
            naive=False,
            use_llm=False,
        )
        blob = profit.answer.text + " " + " ".join(c.chunk.text for c in profit.retrieval.chunks)
        self.assertIn("$186,400", blob)

    def test_gm_cannot_read_own_pay_plan_through_the_assistant(self):
        result = self.engine.ask(
            "patricia",
            "What is the general manager pay plan at Lakeside Honda?",
            naive=False,
            use_llm=False,
        )
        combined = result.answer.text + " " + " ".join(i.chunk.text for i in result.retrieval.chunks)
        self.assertNotIn("$185,000", combined)
        self.assertNotIn("$241,000", combined)
        self.assertNotIn("hr-pay-plan-gm-honda", {i.chunk.doc_id for i in result.retrieval.chunks})


class AnswerQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = _engine()

    def test_holiday_question_cites_the_schedule_for_a_service_advisor(self):
        result = self.engine.ask(
            "maya",
            "When is the group closed for Thanksgiving and the Friday after?",
            naive=False,
            use_llm=False,
        )
        self.assertFalse(result.answer.refusal)
        self.assertIn("November 26", result.answer.text)
        self.assertTrue(result.answer.citations)
        self.assertIn("policy-holidays-2026", {c.doc_id for c in result.answer.citations})

    def test_airbag_bulletin_is_retrievable_by_honda_advisor(self):
        result = self.engine.ask(
            "maya",
            "What is the airbag inflator recall procedure at Lakeside Honda?",
            naive=False,
            use_llm=False,
        )
        self.assertFalse(result.answer.refusal)
        blob = result.answer.text
        self.assertTrue("26V-441" in blob or "inflator" in blob.lower())
        self.assertIn("svc-bulletin-honda-airbag", {c.doc_id for c in result.answer.citations} | {i.chunk.doc_id for i in result.retrieval.chunks})


if __name__ == "__main__":
    unittest.main()
