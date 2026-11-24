"""ACL filter correctness per role, store, department, and sensitivity."""

from __future__ import annotations

import unittest

from securerag.acl import denial_reasons, user_can_read
from securerag.corpus import load_documents
from securerag.users import get_user

DOCS = {d.id: d for d in load_documents()}


def _can(user_id: str, doc_id: str) -> bool:
    return user_can_read(get_user(user_id), DOCS[doc_id])


class HandbookAndPublicTests(unittest.TestCase):
    def test_every_user_can_read_handbook_and_holiday_schedule(self):
        for user_id in ("maya", "chris", "patricia", "derek", "lauren", "jonathan"):
            self.assertTrue(_can(user_id, "policy-handbook"), user_id)
            self.assertTrue(_can(user_id, "policy-holidays-2026"), user_id)
            self.assertTrue(_can(user_id, "policy-pto"), user_id)


class ServiceAdvisorTests(unittest.TestCase):
    """Maya Chen — Service Advisor at Lakeside Honda, clearance=internal."""

    def test_maya_can_read_honda_service_and_store_flash(self):
        self.assertTrue(_can("maya", "svc-bulletin-honda-airbag"))
        self.assertTrue(_can("maya", "svc-csi-honda"))
        self.assertTrue(_can("maya", "store-sales-flash-honda"))
        self.assertTrue(_can("maya", "policy-warranty"))

    def test_maya_cannot_read_financials_or_other_stores(self):
        forbidden = [
            "pl-honda-2026-10",
            "pl-toyota-2026-10",
            "pl-group-consolidated-2026-10",
            "fi-deal-honda-ruiz",
            "fi-deal-toyota-patel",
            "fi-report-honda-october",
            "store-advertising-honda",
            "store-inventory-honda",
            "svc-parts-obsolescence-honda",
            "store-sales-flash-toyota",
            "svc-bulletin-toyota-hybrid",
        ]
        for doc_id in forbidden:
            self.assertFalse(_can("maya", doc_id), doc_id)

    def test_maya_cannot_read_exec_comp_or_pay_plans(self):
        for doc_id in (
            "hr-exec-comp-q3-2026",
            "hr-pay-plan-gm-honda",
            "hr-pay-plan-gm-toyota",
            "exec-bonus-accrual",
            "hr-investigation-miles",
        ):
            self.assertFalse(_can("maya", doc_id), doc_id)
            self.assertTrue(denial_reasons(get_user("maya"), DOCS[doc_id]))


class FiManagerTests(unittest.TestCase):
    """Chris Alvarez — F&I Manager at Lakeside Toyota, clearance=confidential."""

    def test_chris_can_read_toyota_fi_but_not_honda_or_exec(self):
        self.assertTrue(_can("chris", "fi-deal-toyota-patel"))
        self.assertTrue(_can("chris", "fi-report-toyota-october"))
        self.assertTrue(_can("chris", "fi-rate-exception-toyota"))
        self.assertFalse(_can("chris", "fi-deal-honda-ruiz"))
        self.assertFalse(_can("chris", "pl-honda-2026-10"))
        self.assertFalse(_can("chris", "pl-toyota-2026-10"))  # F&I manager is not on the P&L list
        self.assertFalse(_can("chris", "hr-exec-comp-q3-2026"))
        self.assertFalse(_can("chris", "hr-pay-plan-gm-toyota"))


class GeneralManagerTests(unittest.TestCase):
    def test_honda_gm_sees_honda_pl_not_toyota_or_exec(self):
        self.assertTrue(_can("patricia", "pl-honda-2026-10"))
        self.assertTrue(_can("patricia", "fi-deal-honda-ruiz"))
        self.assertTrue(_can("patricia", "svc-bulletin-honda-airbag"))
        self.assertTrue(_can("patricia", "legal-complaint-honda"))
        self.assertFalse(_can("patricia", "pl-toyota-2026-10"))
        self.assertFalse(_can("patricia", "fi-deal-toyota-patel"))
        self.assertFalse(_can("patricia", "hr-pay-plan-gm-honda"))
        self.assertFalse(_can("patricia", "hr-exec-comp-q3-2026"))
        self.assertFalse(_can("patricia", "pl-group-consolidated-2026-10"))

    def test_toyota_gm_sees_toyota_pl_not_honda(self):
        self.assertTrue(_can("derek", "pl-toyota-2026-10"))
        self.assertTrue(_can("derek", "fi-deal-toyota-patel"))
        self.assertFalse(_can("derek", "pl-honda-2026-10"))
        self.assertFalse(_can("derek", "fi-deal-honda-ruiz"))
        self.assertFalse(_can("derek", "hr-pay-plan-gm-toyota"))


class GroupExecTests(unittest.TestCase):
    def test_cfo_sees_financials_and_comp_but_not_hr_investigation(self):
        self.assertTrue(_can("jonathan", "pl-honda-2026-10"))
        self.assertTrue(_can("jonathan", "pl-toyota-2026-10"))
        self.assertTrue(_can("jonathan", "pl-ford-2026-10"))
        self.assertTrue(_can("jonathan", "pl-group-consolidated-2026-10"))
        self.assertTrue(_can("jonathan", "hr-exec-comp-q3-2026"))
        self.assertTrue(_can("jonathan", "hr-pay-plan-gm-honda"))
        self.assertTrue(_can("jonathan", "fi-deal-toyota-patel"))
        self.assertTrue(_can("jonathan", "exec-acquisition-terms"))
        self.assertTrue(_can("jonathan", "legal-hold-finance-charge"))
        self.assertFalse(_can("jonathan", "hr-investigation-miles"))

    def test_hr_director_sees_comp_and_investigation_not_pl_or_deals(self):
        self.assertTrue(_can("lauren", "hr-exec-comp-q3-2026"))
        self.assertTrue(_can("lauren", "hr-pay-plan-gm-honda"))
        self.assertTrue(_can("lauren", "hr-pay-plan-gm-toyota"))
        self.assertTrue(_can("lauren", "hr-investigation-miles"))
        self.assertTrue(_can("lauren", "hr-headcount-october"))
        self.assertFalse(_can("lauren", "pl-honda-2026-10"))
        self.assertFalse(_can("lauren", "pl-group-consolidated-2026-10"))
        self.assertFalse(_can("lauren", "fi-deal-toyota-patel"))
        self.assertFalse(_can("lauren", "exec-acquisition-terms"))

    def test_group_store_wildcard_lets_cfo_into_store_tagged_docs_when_role_matches(self):
        # CFO is store=group, role=cfo, so a Honda-only P&L that lists cfo is visible.
        self.assertEqual(get_user("jonathan").store, "group")
        self.assertTrue(_can("jonathan", "pl-honda-2026-10"))
        # A Honda sales flash allows any role, so the CFO can also see it.
        self.assertTrue(_can("jonathan", "store-sales-flash-honda"))


class SensitivityAndDepartmentTests(unittest.TestCase):
    def test_internal_clearance_blocks_confidential_even_if_other_fields_were_open(self):
        # Maya's clearance is internal; Honda P&L is confidential (and also role-blocked).
        reasons = denial_reasons(get_user("maya"), DOCS["pl-honda-2026-10"])
        self.assertIn("sensitivity", reasons)
        self.assertIn("role", reasons)

    def test_department_rule_blocks_cfo_only_finance_file_from_wrong_dept_when_role_wrong(self):
        # Group P&L is cfo-only and finance department. HR director fails role and department.
        reasons = denial_reasons(get_user("lauren"), DOCS["pl-group-consolidated-2026-10"])
        self.assertIn("role", reasons)
        self.assertIn("department", reasons)


if __name__ == "__main__":
    unittest.main()
