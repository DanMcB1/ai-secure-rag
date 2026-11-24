"""Fictional Lakeside Auto Group document corpus.

Every document is sample data, clearly about a made-up dealer group.
Each one carries ACL metadata (roles, departments, stores, sensitivity).
"""

from __future__ import annotations

from .models import Document

# Short aliases so the table below stays readable.
ANY = ("any",)
HONDA = ("honda",)
TOYOTA = ("toyota",)
FORD = ("ford",)

# Role groups used on several documents.
ALL_STAFF = ("any",)
MANAGERS_HR = ("gm", "hr_director", "cfo")
FINANCE_READERS = ("gm", "cfo", "controller")
FI_STORE = ("fi_manager", "gm", "cfo", "controller")
SERVICE_STORE = ("service_advisor", "service_manager", "gm", "cfo")
HR_ONLY = ("hr_director",)
HR_AND_CFO = ("hr_director", "cfo")
CFO_ONLY = ("cfo",)
CFO_AND_GM = ("cfo", "gm")
LEGAL_FINANCE = ("cfo",)  # no standalone legal user in this demo


def _doc(
    doc_id: str,
    title: str,
    category: str,
    store_ids: tuple[str, ...],
    departments: tuple[str, ...],
    roles: tuple[str, ...],
    sensitivity: str,
    body: str,
) -> Document:
    return Document(
        id=doc_id,
        title=title,
        category=category,
        store_ids=store_ids,
        departments=departments,
        roles=roles,
        sensitivity=sensitivity,
        body=body.strip() + "\n",
    )


def load_documents() -> list[Document]:
    return list(DOCUMENTS)


# ---------------------------------------------------------------------------
# 48 sample documents
# ---------------------------------------------------------------------------

DOCUMENTS: list[Document] = [
    # ---- Company policies (internal / public, any store, any role) ----
    _doc(
        "policy-handbook",
        "Employee handbook excerpt — Lakeside Auto Group",
        "policy",
        ANY,
        ANY,
        ALL_STAFF,
        "internal",
        """
This excerpt is from the Lakeside Auto Group employee handbook (sample). It applies to staff at Lakeside Honda, Lakeside Toyota, and Lakeside Ford.

The group expects every employee to treat customers and coworkers with respect, to follow the lawful instructions of a manager, and to protect customer information in the deal jacket, the DMS, and any paper or electronic file.

Pay is issued biweekly. Questions about a paycheck should go first to the office manager at your store, then to Human Resources at the group office. This handbook does not create a contract of employment.

If you are not sure whether a document or a screen is something you are allowed to share, ask your manager before you send it. Customer credit data, deal jackets, and personnel files are never casual reading.
""",
    ),
    _doc(
        "policy-pto",
        "Paid time off policy",
        "policy",
        ANY,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Auto Group paid time off (sample policy, calendar year 2026).

Full-time employees accrue 10 days of paid time off in years one and two, 15 days beginning in year three, and 20 days beginning in year eight. Unused days may carry over up to five days into the next calendar year. Requests of three or more consecutive days should be submitted two weeks in advance, except for illness.

Store managers approve time off for their teams. The group office publishes a blackout calendar around month-end close and the last Saturday before a manufacturer month-end.

Part-time employees accrue PTO at half the full-time rate after 90 days.
""",
    ),
    _doc(
        "policy-it-use",
        "IT acceptable use policy",
        "policy",
        ANY,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Auto Group IT acceptable use policy (sample).

Company email, the DMS, the CRM, and any AI assistant the group provides are for business use. Do not forward deal jackets, credit applications, or payroll files to a personal email address. Do not paste customer Social Security numbers, full card numbers, or unredacted deal documents into a public chatbot.

Personal phones may be used on the drive, but photographs of a customer's license, credit application, or check are not allowed. Lost badges and suspected phishing should be reported to IT the same day.

The group may review activity on company systems when there is a business or legal reason to do so.
""",
    ),
    _doc(
        "policy-holidays-2026",
        "Holiday schedule 2026",
        "policy",
        ANY,
        ANY,
        ALL_STAFF,
        "public",
        """
Lakeside Auto Group holiday schedule for 2026 (sample). All three stores follow the same close calendar unless a store GM posts a local change.

Closed: New Year's Day (Thursday, January 1), Memorial Day (Monday, May 25), Independence Day (Saturday, July 4 — the stores close Friday, July 3 at 5 p.m. and reopen Monday, July 6), Labor Day (Monday, September 7), Thanksgiving Day (Thursday, November 26), and Christmas Day (Friday, December 25).

The stores are open the Friday after Thanksgiving (November 27) with sales and service both running a regular Saturday-style schedule. Christmas Eve and New Year's Eve the showrooms close at 3 p.m.; service closes at 2 p.m.

This schedule is posted for all staff and may be shared with customers.
""",
    ),
    _doc(
        "policy-privacy-glba",
        "Customer privacy and GLBA staff notice",
        "policy",
        ANY,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Auto Group staff notice on customer privacy (sample). The group handles nonpublic personal information in F&I and, at times, in service and sales.

Do not discuss a customer's credit, income, or deal structure on the drive or in a waiting lounge. Printouts of a credit application or a menu should be retrieved from the printer immediately and locked in the deal jacket when not in use.

If a customer asks for a copy of their own deal documents, follow the office procedure. If anyone else asks — including a spouse who is not on the contract, another store, or a third-party "helper" — stop and call the office manager or the Controller.

This notice is a reminder, not a substitute for the group's written privacy policy or any required annual training.
""",
    ),
    _doc(
        "policy-safety",
        "Workplace safety policy",
        "policy",
        ANY,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Auto Group workplace safety policy (sample).

Shop staff must wear required eye and foot protection in the stall area. Lift locks must be engaged before walking under a vehicle. Used oil, antifreeze, and battery waste go only in marked containers.

On the lot, no customer sits in a vehicle that is being moved by a porter unless a manager has approved a specific exception. Cell phone use while operating a company vehicle on the lot is not allowed.

Injuries, near misses, and damaged customer vehicles are reported to the store GM the same day, with a copy to the group office. First-aid kits are in the shop break room and the receptionist desk at each store.
""",
    ),
    _doc(
        "policy-warranty",
        "Group new-vehicle warranty handling guide",
        "service",
        ANY,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Auto Group warranty handling guide (sample). This guide is for service advisors, service managers, and store leadership.

New vehicles follow the manufacturer's bumper-to-bumper coverage of 3 years or 36,000 miles, whichever comes first, unless the manufacturer has published a different term for that model. Powertrain terms are listed on the window sticker and in the service DMS.

A warranty repair order must include the customer concern, the cause, the correction, and the authorization number when the manufacturer requires one. Do not promise a loaner on a warranty visit until the service manager has confirmed availability.

Goodwill after warranty expiration is a service-manager decision under the store's monthly cap, and is not something an advisor should quote on the drive.
""",
    ),
    # ---- HR (mix of internal, confidential, restricted) ----
    _doc(
        "hr-benefits-2026",
        "Open enrollment benefits guide 2026",
        "hr",
        ANY,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Auto Group open enrollment guide for plan year 2026 (sample). Enrollment runs November 3 through November 14, 2026. Coverage changes take effect January 1, 2027.

Medical plan options are the standard PPO and a high-deductible plan with a group HSA contribution of $600 for employee-only coverage and $1,000 for family coverage. Dental and vision are offered as a bundled buy-up. Short-term disability is company-paid for full-time staff.

Questions about a specific claim or a dependents audit should go to Human Resources, not to your store office manager. This guide does not include executive supplemental plans or individual compensation.
""",
    ),
    _doc(
        "hr-review-process",
        "Annual performance review process for managers",
        "hr",
        ANY,
        ANY,
        MANAGERS_HR,
        "confidential",
        """
Lakeside Auto Group performance review process (sample). This document is for managers, the HR Director, and the CFO.

Reviews for 2026 performance are due to Human Resources by Friday, January 16, 2027. Ratings use a four-point scale: exceeds, meets, developing, and does not meet. A "does not meet" rating requires a written performance plan and an HR review before it is delivered.

Managers should not discuss another employee's rating, pay change, or performance plan with anyone other than that employee, the GM, and Human Resources. Merit pool guidance is issued separately by the group office and is not part of this process document.
""",
    ),
    _doc(
        "hr-disciplinary-managers",
        "Disciplinary policy for store managers",
        "hr",
        ANY,
        ANY,
        MANAGERS_HR,
        "confidential",
        """
Lakeside Auto Group disciplinary policy for managers (sample).

Coaching conversations may be informal. Written warnings, final warnings, and involuntary separations for a manager or a department head must be reviewed by the HR Director before they are delivered. A GM may send an employee home for the day when safety or customer conduct requires it, and must notify Human Resources within four hours.

Documentation belongs in the personnel file maintained by Human Resources, not in a personal email folder or a shared store drive. This policy does not cover executive employment agreements.
""",
    ),
    _doc(
        "hr-exec-comp-q3-2026",
        "Executive compensation memo — Q3 2026",
        "executive",
        ANY,
        ANY,
        HR_AND_CFO,
        "restricted",
        """
Lakeside Auto Group executive compensation memo, Q3 2026 (sample — fictional figures). Distribution is limited to the CFO and the HR Director.

Elena Voss, Group Chief Executive Officer, has a 2026 base salary of $310,000 and a target bonus of 40 percent of base ($124,000), for on-target earnings of $434,000. Her long-term grant for 2026 is a $75,000 cash-settled phantom unit with a three-year vest.

Jonathan Hale, Chief Financial Officer, has a 2026 base salary of $265,000 and a target bonus of 30 percent of base ($79,500), for on-target earnings of $344,500.

Lauren Brooks, HR Director, has a 2026 base salary of $175,000 and a target bonus of 20 percent of base ($35,000), for on-target earnings of $210,000.

No store-level employee, including a general manager, is authorized to receive this memo. Bonus payouts for 2026 will be calculated after the year-end audit and are not guaranteed.
""",
    ),
    _doc(
        "hr-pay-plan-gm-honda",
        "General Manager pay plan — Lakeside Honda — 2026",
        "executive",
        HONDA,
        ANY,
        HR_AND_CFO,
        "restricted",
        """
Lakeside Honda General Manager pay plan for calendar year 2026 (sample — fictional figures). This plan applies to Patricia Walsh, General Manager of Lakeside Honda. Distribution is limited to the CFO and the HR Director.

Base salary is $185,000, paid biweekly. The variable plan is 2.1 percent of the store's departmental gross (new, used, F&I, service, and parts combined), paid monthly. A volume bonus of $12,000 is earned if the store retails 180 new units in a quarter. A CSI kicker of $8,000 is earned if the manufacturer's combined sales and service CSI is at or above the zone average for the quarter.

On-target earnings under this plan are $241,000, assuming departmental gross and CSI at the 2026 budget. The plan does not include a group equity grant. Patricia Walsh is not copied on this file; Human Resources delivers the signed plan separately.
""",
    ),
    _doc(
        "hr-pay-plan-gm-toyota",
        "General Manager pay plan — Lakeside Toyota — 2026",
        "executive",
        TOYOTA,
        ANY,
        HR_AND_CFO,
        "restricted",
        """
Lakeside Toyota General Manager pay plan for calendar year 2026 (sample — fictional figures). This plan applies to Derek Singh, General Manager of Lakeside Toyota. Distribution is limited to the CFO and the HR Director.

Base salary is $192,000, paid biweekly. The variable plan is 2.0 percent of the store's departmental gross, paid monthly. A volume bonus of $14,000 is earned at 200 new retail units in a quarter. A CSI kicker of $8,000 uses the same zone-average rule as the other stores.

On-target earnings under this plan are $255,000, assuming departmental gross and CSI at the 2026 budget. Derek Singh is not copied on this file.
""",
    ),
    _doc(
        "hr-pay-plan-gm-ford",
        "General Manager pay plan — Lakeside Ford — 2026",
        "executive",
        FORD,
        ANY,
        HR_AND_CFO,
        "restricted",
        """
Lakeside Ford General Manager pay plan for calendar year 2026 (sample — fictional figures). This plan applies to Angela Ruiz, General Manager of Lakeside Ford. Distribution is limited to the CFO and the HR Director.

Base salary is $170,000. The variable plan is 2.2 percent of departmental gross. A volume bonus of $10,000 is earned at 150 new retail units in a quarter. A CSI kicker of $6,000 applies if Ford's combined CSI is at or above the region average.

On-target earnings under this plan are $228,000 at budget. Angela Ruiz is not copied on this file.
""",
    ),
    _doc(
        "hr-investigation-miles",
        "Confidential HR investigation note — R. Miles",
        "hr",
        HONDA,
        ("hr",),
        HR_ONLY,
        "restricted",
        """
Confidential Human Resources investigation note (sample — fictional). This note is visible only to the HR Director.

Matter HR-2026-17 concerns an employee identified as R. Miles at Lakeside Honda. The allegation is unprofessional conduct toward a coworker in the service cashier area on October 9, 2026. Human Resources opened the file on October 10.

Interviews were completed on October 15. The recommended next step is a written warning and a mandatory conduct refresher, pending a final conversation with the Honda General Manager. No customer complaint is attached to this file.

This note must not be placed on a shared store drive or summarized in a group email.
""",
    ),
    _doc(
        "hr-headcount-october",
        "Headcount and open requisitions — October 2026",
        "hr",
        ANY,
        ANY,
        HR_AND_CFO,
        "confidential",
        """
Lakeside Auto Group headcount snapshot as of October 31, 2026 (sample). Distribution is the HR Director and the CFO. Store GMs receive a store-only extract in a separate file, not this combined view.

Group headcount is 214 employees: Lakeside Honda 78, Lakeside Toyota 86, Lakeside Ford 41, and group office 9. Open requisitions: two Honda technicians, one Toyota BDC representative, one Ford porter, and a group-office staff accountant.

Year-to-date turnover is 18 percent, highest in Honda service porters. Overtime hours in service were 6.4 percent of service payroll in October, down from 7.1 percent in September.
""",
    ),
    _doc(
        "hr-headcount-honda-extract",
        "Honda store headcount extract — October 2026",
        "hr",
        HONDA,
        ANY,
        MANAGERS_HR,
        "confidential",
        """
Lakeside Honda headcount extract as of October 31, 2026 (sample). This extract is for the Honda GM, the HR Director, and the CFO. It does not include pay rates.

Honda headcount is 78: sales 22, F&I 4, service 28, parts 8, office and porters 16. Open requisitions at this store: two technicians (one A-tech, one express lube). Three employees are currently on approved leave.

This extract does not include the R. Miles investigation or any pay-plan figures.
""",
    ),
    # ---- F&I deal memos and reports ----
    _doc(
        "fi-deal-honda-ruiz",
        "F&I deal memo — Ruiz, Lakeside Honda, deal H-2094",
        "fi",
        HONDA,
        ANY,
        FI_STORE,
        "confidential",
        """
F&I deal memo (sample — fictional customers and figures). Lakeside Honda deal H-2094. Customers: Eva and Luis Ruiz. Vehicle: 2026 Honda CR-V EX-L, stock H-4412.

Selling price is $36,420. The contract is a 72-month retail installment sale at 6.49 percent APR through the captive. Front-end gross is $2,180. F&I products: vehicle service contract $2,295, GAP $895, and paint-and-fabric protection $699. Finance reserve is $1,620. Backend gross on this deal is $2,870.

The deal was desked by the Honda F&I manager on November 8, 2026 and funded on November 12. A rate exception was not required. This memo is part of the deal jacket and is limited to F&I, the Honda GM, and finance leadership.
""",
    ),
    _doc(
        "fi-deal-honda-chen",
        "F&I deal memo — Chen lease, Lakeside Honda, deal H-2110",
        "fi",
        HONDA,
        ANY,
        FI_STORE,
        "confidential",
        """
F&I deal memo (sample — fictional). Lakeside Honda deal H-2110. Customer: Priya Chen (no relation to any group employee). Vehicle: 2026 Honda Accord Touring, stock H-4479, 36-month lease, 12,000 miles per year.

Capitalized cost is $38,110 after cap-cost reduction of $2,000. Money factor is a buy-rate plus a 0.00015 markup. Acquisition fee $695. F&I products: excess-wear waiver $795 and prepaid maintenance $1,149. Backend gross is $1,420. No GAP was sold on the lease.

The Honda desk approved a $750 cap-cost reduction from dealership cash to close a payment objection. This memo is limited to Honda F&I, the Honda GM, and finance leadership.
""",
    ),
    _doc(
        "fi-deal-toyota-patel",
        "F&I deal memo — Patel, Lakeside Toyota, deal T-4821",
        "fi",
        TOYOTA,
        ANY,
        FI_STORE,
        "confidential",
        """
F&I deal memo (sample — fictional customers and figures). Lakeside Toyota deal T-4821. Customers: Amira and Dev Patel. Vehicle: 2026 Toyota Prius LE, stock T-3308.

Selling price is $34,680. The contract is a 60-month retail installment sale at 5.99 percent APR. Front-end gross is $1,940. F&I products sold: vehicle service contract $2,195, GAP $895, and appearance protection $799. Finance reserve is $1,140. Backend gross on the Patel deal is $2,410.

The deal was written on November 14, 2026 and funded on November 18. Chris Alvarez, F&I Manager at Lakeside Toyota, desked the menu. This memo is limited to Toyota F&I, the Toyota GM, and finance leadership. It is not shared with other stores.
""",
    ),
    _doc(
        "fi-deal-toyota-williams",
        "F&I deal memo — Williams, Lakeside Toyota, deal T-4790",
        "fi",
        TOYOTA,
        ANY,
        FI_STORE,
        "confidential",
        """
F&I deal memo (sample — fictional). Lakeside Toyota deal T-4790. Customer: Jordan Williams. Vehicle: 2025 Toyota RAV4 XLE, used certified, stock T-3194.

Selling price is $31,200. 72-month contract at 7.19 percent APR. A rate mark-up of 0.75 percent over buy rate produced a finance reserve of $1,880. Products: VSC $2,495 and GAP $895. Backend gross is $3,190. The customer declined tire-and-wheel.

A funding condition from the lender asked for a proof-of-residence update; the deal funded on November 6, 2026 after that was scanned into the jacket. Limited to Toyota F&I, the Toyota GM, and finance leadership.
""",
    ),
    _doc(
        "fi-deal-ford-nguyen",
        "F&I deal memo — Nguyen, Lakeside Ford, deal F-1188",
        "fi",
        FORD,
        ANY,
        FI_STORE,
        "confidential",
        """
F&I deal memo (sample — fictional). Lakeside Ford deal F-1188. Customer: Hannah Nguyen. Vehicle: 2026 Ford F-150 XLT SuperCrew, stock F-2088.

Selling price is $52,640. 72-month contract at 6.74 percent APR. Front-end gross is $3,050. Products: VSC $2,695, GAP $995, and rust protection $599. Finance reserve is $2,040. Backend gross is $3,490.

The deal funded November 10, 2026. This memo stays at Lakeside Ford F&I, the Ford GM, and finance leadership.
""",
    ),
    _doc(
        "fi-report-honda-october",
        "F&I monthly product report — Lakeside Honda — October 2026",
        "fi",
        HONDA,
        ANY,
        FI_STORE,
        "confidential",
        """
Lakeside Honda F&I product report for October 2026 (sample). For Honda F&I, the Honda GM, and finance leadership.

Honda F&I gross for October is $312,000. Retail finance contracts: 94. Average backend per retail deal: $1,870. VSC penetration 54 percent, GAP 61 percent, appearance protection 28 percent. Chargebacks in the month were $6,400, mainly two cancelled service contracts.

Finance reserve totaled $71,200. One captive rate exception above 50 basis points was approved by the Honda GM on deal H-1988. This report is not a P&L and does not include store net profit.
""",
    ),
    _doc(
        "fi-report-toyota-october",
        "F&I monthly product report — Lakeside Toyota — October 2026",
        "fi",
        TOYOTA,
        ANY,
        FI_STORE,
        "confidential",
        """
Lakeside Toyota F&I product report for October 2026 (sample). For Toyota F&I, the Toyota GM, and finance leadership.

Toyota F&I gross for October is $348,500. Retail finance contracts: 108. Average backend per retail deal: $1,995. VSC penetration 58 percent, GAP 64 percent. Chargebacks were $4,150.

Finance reserve totaled $84,900. No rate exception above 50 basis points was approved in October. This report is not shared with other rooftops.
""",
    ),
    _doc(
        "fi-rate-exception-toyota",
        "Rate exception log — Lakeside Toyota — fall 2026",
        "fi",
        TOYOTA,
        ANY,
        FI_STORE,
        "confidential",
        """
Lakeside Toyota rate exception log, September through mid-November 2026 (sample). Limited to Toyota F&I, the Toyota GM, and finance leadership.

September: two exceptions, both 25 basis points, deals T-4611 and T-4630, approved by Derek Singh. October: none above 50 basis points. November through the 18th: one 25-basis-point exception on deal T-4802 for a repeat customer, approved by the Toyota GM.

A rate exception does not, by itself, change reserve policy. Any exception above 75 basis points requires a note in the deal jacket and a same-day email to the Controller.
""",
    ),
    _doc(
        "fi-chargeback-honda",
        "F&I chargeback memo — Lakeside Honda — November 2026",
        "fi",
        HONDA,
        ANY,
        FI_STORE,
        "confidential",
        """
Lakeside Honda F&I chargeback memo (sample). Limited to Honda F&I, the Honda GM, and finance leadership.

On November 4, 2026 the administrator cancelled the vehicle service contract on deal H-1872 (customer name withheld here) after a customer rescission within the cancellation window. The chargeback is $1,280, to be posted against November F&I gross.

A second chargeback of $640 for a GAP cancellation on deal H-1901 will post in the same week. Advisors should not quote a refund amount to a customer until F&I has the administrator worksheet.
""",
    ),
    # ---- Store P&Ls and group finance ----
    _doc(
        "pl-honda-2026-10",
        "Store P&L — Lakeside Honda — October 2026",
        "pl",
        HONDA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Honda monthly P&L for October 2026 (sample — fictional figures). Distribution is the Honda General Manager, the CFO, and the Controller. Other store GMs and department employees do not receive this file.

October revenue is $4,820,000. Departmental gross: new $410,000, used $265,000, F&I $312,000, service $198,000, parts $121,000. Total departmental gross is $1,306,000. Operating expenses are $1,119,600. Lakeside Honda's net profit in October is $186,400.

New units retailed: 162. Used units: 94. Service absorption for the month is 82 percent. Year-to-date net profit through October is $1,742,000, which is $64,000 ahead of budget.
""",
    ),
    _doc(
        "pl-toyota-2026-10",
        "Store P&L — Lakeside Toyota — October 2026",
        "pl",
        TOYOTA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Toyota monthly P&L for October 2026 (sample — fictional figures). Distribution is the Toyota General Manager, the CFO, and the Controller.

October revenue is $5,140,000. Departmental gross: new $455,000, used $288,000, F&I $348,500, service $210,000, parts $132,000. Total departmental gross is $1,433,500. Operating expenses are $1,221,600. Lakeside Toyota's net profit in October is $211,900.

New units retailed: 181. Used units: 102. Service absorption is 84 percent. Year-to-date net profit through October is $2,018,000, $112,000 ahead of budget.
""",
    ),
    _doc(
        "pl-ford-2026-10",
        "Store P&L — Lakeside Ford — October 2026",
        "pl",
        FORD,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Ford monthly P&L for October 2026 (sample — fictional figures). Distribution is the Ford General Manager, the CFO, and the Controller.

October revenue is $3,960,000. Departmental gross: new $302,000, used $198,000, F&I $241,000, service $154,000, parts $96,000. Total departmental gross is $991,000. Operating expenses are $848,800. Lakeside Ford's net profit in October is $142,200.

New units retailed: 128. Used units: 71. Service absorption is 79 percent. Year-to-date net profit through October is $1,155,000, $21,000 behind budget.
""",
    ),
    _doc(
        "pl-honda-dept-gross",
        "Departmental gross detail — Lakeside Honda — October 2026",
        "pl",
        HONDA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Honda departmental gross detail, October 2026 (sample). For the Honda GM, the CFO, and the Controller.

New-vehicle gross of $410,000 includes a $38,000 holdback estimate and $22,000 in manufacturer bonuses. Used-vehicle gross of $265,000 is after a $14,500 pack. F&I gross of $312,000 matches the F&I product report. Service gross of $198,000 is customer-pay plus warranty; internal work is eliminated at group level in the consolidated file.

Parts gross of $121,000 includes $18,000 of wholesale. This detail supports the store P&L and is not a substitute for it.
""",
    ),
    _doc(
        "pl-toyota-dept-gross",
        "Departmental gross detail — Lakeside Toyota — October 2026",
        "pl",
        TOYOTA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Toyota departmental gross detail, October 2026 (sample). For the Toyota GM, the CFO, and the Controller.

New-vehicle gross of $455,000 includes $44,000 holdback and $26,500 in manufacturer bonuses. Used-vehicle gross of $288,000 is after a $16,000 pack. F&I gross of $348,500 matches the Toyota F&I product report. Service gross is $210,000. Parts gross is $132,000, including $21,000 wholesale.

Advertising of $64,000 for the month is in operating expenses, not in this gross file.
""",
    ),
    _doc(
        "pl-group-consolidated-2026-10",
        "Group consolidated P&L — October 2026",
        "pl",
        ANY,
        ("finance",),
        CFO_ONLY,
        "restricted",
        """
Lakeside Auto Group consolidated P&L for October 2026 (sample — fictional figures). This file is limited to the CFO. It is not sent to store general managers, who receive only their own store P&L.

October group revenue is $13,920,000. Combined departmental gross is $3,730,500. Group office and allocated expenses are $320,000. October group net profit is $540,500, which is the sum of Honda $186,400, Toyota $211,900, Ford $142,200, less $0 of residual group items after allocation in this sample.

Year-to-date group net profit through October is $4,915,000, $155,000 ahead of budget. Cash on hand at month end is $6,400,000, including a $1,200,000 manufacturer reserve that is not available for distribution.
""",
    ),
    # ---- Service bulletins and store service reports ----
    _doc(
        "svc-bulletin-honda-airbag",
        "Service bulletin — Honda airbag inflator recall 26V-441",
        "service",
        HONDA,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Honda service bulletin (sample). Recall 26V-441, driver airbag inflator, 2019–2021 Honda Accord.

Advisors should check every 2019, 2020, and 2021 Accord against the manufacturer campaign screen at write-up, even if the customer is in for an oil change. If the VIN is open on 26V-441, schedule the inflator replacement before other express work when parts are on the shelf.

American Honda lists a typical customer wait of 2.5 hours when the inflator is in stock. Do not install an aftermarket inflator. If the part is on national backorder, set a parts-alert on the repair order and offer a rental only with service-manager approval.

As of November 18, 2026, Lakeside Honda has 23 open VINs in its service base and 14 inflators on the shelf. This bulletin is for Honda service staff and Honda leadership. It does not include store financials.
""",
    ),
    _doc(
        "svc-bulletin-toyota-hybrid",
        "Service bulletin — Toyota hybrid battery inspection campaign",
        "service",
        TOYOTA,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Toyota service bulletin (sample). Hybrid battery inspection campaign for certain 2020–2022 Prius and RAV4 Hybrid vehicles.

Advisors should run the campaign inquiry at write-up. If the inspection flags a high-voltage battery replacement, do not quote a customer-pay price; this campaign is manufacturer-covered when the VIN is open. Typical bay time is 4.0 hours for a replacement and 0.8 hours for an inspection only.

As of November 18, 2026, Lakeside Toyota has 11 open campaign VINs and two loaner hybrids reserved for battery replacements. Aftermarket or used high-voltage batteries are not approved on campaign repairs.
""",
    ),
    _doc(
        "svc-bulletin-ford-transmission",
        "Service bulletin — Ford 10-speed transmission adaptive-shift reflash",
        "service",
        FORD,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Ford service bulletin (sample). Technical service bulletin for a 10-speed automatic adaptive-shift reflash on certain 2023–2025 F-150 units with a customer concern of harsh 3–4 upshift.

Confirm the concern on a road test, then apply the latest PCM calibration listed in the OEM service information. Typical billed time is 0.9 hours. A transmission replacement is not authorized by this bulletin.

If the concern remains after the reflash, open a technical assistance case before any internal teardown. This bulletin is for Ford service staff and Ford leadership.
""",
    ),
    _doc(
        "svc-csi-honda",
        "Service CSI and hours report — Lakeside Honda — October 2026",
        "service",
        HONDA,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Honda service CSI and hours report, October 2026 (sample). For Honda service advisors, the service manager, the Honda GM, and the CFO.

Honda service CSI for October is 89.4, two points above the zone average. Average repair-order cycle time is 2.1 days. Customer-pay hours: 1,842. Warranty hours: 610. Comeback rate: 3.1 percent.

The most common CSI detractor in the comments is "waited for a part that was promised the same day." Advisors should not promise same-day parts without a confirmed parts-ticket status.
""",
    ),
    _doc(
        "svc-csi-toyota",
        "Service CSI and hours report — Lakeside Toyota — October 2026",
        "service",
        TOYOTA,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Toyota service CSI and hours report, October 2026 (sample). For Toyota service staff, the Toyota GM, and the CFO.

Toyota service CSI for October is 91.1, three points above the region average. Average repair-order cycle time is 1.8 days. Customer-pay hours: 2,040. Warranty hours: 540. Comeback rate: 2.4 percent.

Express lane average wait at drop-off was 11 minutes. The service manager is holding a Saturday express experiment through December.
""",
    ),
    _doc(
        "svc-cycle-honda",
        "Repair-order cycle time memo — Lakeside Honda",
        "service",
        HONDA,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Honda repair-order cycle time memo (sample), written November 6, 2026.

Average cycle time of 2.1 days in October is 0.3 days slower than September. The delay is concentrated in jobs waiting on body-color touch-up and on two diagnostic ROs that sat over a weekend without a follow-up call.

Starting November 10, any open RO older than three days appears on the morning dispatch board in red, and the assigned advisor calls the customer before 10 a.m. This is an operations memo, not a financial report.
""",
    ),
    _doc(
        "svc-parts-obsolescence-honda",
        "Parts obsolescence review — Lakeside Honda — Q3 2026",
        "service",
        HONDA,
        ANY,
        ("service_manager", "gm", "cfo"),
        "confidential",
        """
Lakeside Honda parts obsolescence review for third quarter 2026 (sample). For the Honda service manager, the Honda GM, and the CFO. Service advisors do not receive this file.

Obsolete and aged parts over 12 months are valued at $41,600 at cost. The recommended write-down in October is $18,200, with a return attempt on $9,400 of still-eligible Honda parts first. The largest aged item is a leftover special-order body part at $2,760.

This review affects the store P&L when the write-down posts. It is not a customer-facing document.
""",
    ),
    _doc(
        "svc-special-tools",
        "Special service tools list — group",
        "service",
        ANY,
        ANY,
        SERVICE_STORE,
        "internal",
        """
Lakeside Auto Group special service tools list (sample). Shared with service advisors, service managers, and store leadership at all three rooftops.

Honda: airbag inflator fixture kit and alignment calibration target set, kept in the Honda specialty cabinet. Toyota: hybrid insulated-glove kit and high-voltage battery lift table at the south bay. Ford: 10-speed transmission fluid adapter and F-150 front-camera alignment fixture.

Tools do not leave the store without the service manager's sign-out. A missing glove kit or inflator fixture should be reported the same day; loaners from a neighboring Lakeside store are arranged by the service managers, not by advisors calling the other shop directly for a customer promise.
""",
    ),
    # ---- Legal / executive ----
    _doc(
        "legal-hold-finance-charge",
        "Legal hold notice — finance charge inquiry L-2026-14",
        "legal",
        ANY,
        ("finance", "legal"),
        LEGAL_FINANCE,
        "restricted",
        """
Legal hold notice (sample — fictional). Matter L-2026-14, finance-charge class-action inquiry. This notice is limited to the CFO in this demo corpus.

Preserve all F&I menus, rate-exception emails, and deal-jacket scans from January 1, 2024 forward. Do not alter, delete, or auto-purge those records. The hold includes group office files and all three stores.

Outside counsel issued the hold on October 28, 2026. Staff who are not on the hold list should not be briefed on the substance of the inquiry. Questions go to the CFO, not to a store group chat.
""",
    ),
    _doc(
        "legal-fair-lending-review",
        "Fair lending review notes — Q3 2026",
        "legal",
        ANY,
        ("finance",),
        CFO_ONLY,
        "restricted",
        """
Fair lending review notes, third quarter 2026 (sample — fictional). Limited to the CFO.

A quarterly look at contract APR versus buy rate, by store, did not show a dealer-imposed mark-up pattern that the reviewer flagged for immediate escalation. Toyota's average mark-up was 0.41 percent, Honda 0.47 percent, and Ford 0.52 percent. Two deals at Ford (F-1022 and F-1040) were noted for a 1.25 percent mark-up and were already documented with a rate-exception note.

This review is not a legal opinion and is not distributed to F&I managers or store GMs in this form.
""",
    ),
    _doc(
        "legal-complaint-honda",
        "Consumer complaint legal summary — Lakeside Honda — C-2026-09",
        "legal",
        HONDA,
        ANY,
        CFO_AND_GM,
        "confidential",
        """
Consumer complaint legal summary (sample — fictional). File C-2026-09, Lakeside Honda. Visible to the Honda GM and the CFO.

A customer alleged that a documentation fee was not disclosed as discussed on the menu. The deal in question is H-1760, dated August 19, 2026. The menu scan in the jacket shows the fee. The recommended path is a written response and a courtesy review of the product cancellations, not a full unwind, pending the Controller's agreement.

No admission of liability should be made by store staff. Media or attorney letters go to the group office.
""",
    ),
    _doc(
        "exec-board-pack-2027",
        "Board pack excerpt — 2027 growth plan",
        "executive",
        ANY,
        ANY,
        HR_AND_CFO,
        "restricted",
        """
Lakeside Auto Group board pack excerpt (sample — fictional). 2027 growth plan. Limited to the CFO and the HR Director in this corpus.

Management's 2027 plan is to add a CDJR rooftop in the same metro, with a working name of Lakeside Chrysler Dodge Jeep Ram. The draft timeline is a letter of intent in Q1 2027 and a targeted close in Q3 2027 if due diligence holds.

The pack also flags a 2027 headcount increase of 12 at the existing stores, mostly technicians, and a group-office financial analyst role. Store GMs are not copied on this excerpt.
""",
    ),
    _doc(
        "exec-acquisition-terms",
        "Acquisition term-sheet notes — fourth rooftop",
        "executive",
        ANY,
        ("finance",),
        CFO_ONLY,
        "restricted",
        """
Acquisition term-sheet notes (sample — fictional). Fourth rooftop, working name Lakeside CDJR. Limited to the CFO.

The seller's indicated price is $18.5 million for the hard assets and blue-sky combined, with a $2.0 million holdback on blue-sky subject to a 24-month CSI and volume collar. Earnest money in the draft letter of intent is $250,000. Manufacturer approval is a condition precedent.

These figures are negotiating positions, not a signed deal, and must not be discussed with store staff or with anyone at the target store.
""",
    ),
    _doc(
        "exec-bonus-accrual",
        "Bonus accrual — executive team — October 2026",
        "executive",
        ANY,
        ANY,
        HR_AND_CFO,
        "restricted",
        """
Executive bonus accrual through October 2026 (sample — fictional). Limited to the CFO and the HR Director.

Year-to-date accrual toward 2026 target bonuses: Elena Voss $103,300 (on a $124,000 target, reflecting current profit tracking), Jonathan Hale $66,200 (on a $79,500 target), Lauren Brooks $29,200 (on a $35,000 target). Accruals will be trued up after the year-end audit.

Store GM variable pay is accrued on the store P&Ls and is not listed in this executive file.
""",
    ),
    # ---- Per-store operations (some visible more broadly at the store) ----
    _doc(
        "store-sales-flash-honda",
        "Sales flash — Lakeside Honda — month to date November 21, 2026",
        "store",
        HONDA,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Honda sales flash, month to date as of November 21, 2026 (sample). Posted for Honda staff.

Month to date the store has retailed 47 new units and 29 used units. The month-end new-car objective is 155. The weekend forecast is 28 total units if weather holds. This flash does not include gross, reserve, or net profit.

Top unsold aged new units: two Accord hybrids over 90 days. The desk will review them at Monday morning meeting. Service and parts staff may share the unit count with customers who ask how busy the store is; do not quote objectives as a promise of a discount.
""",
    ),
    _doc(
        "store-sales-flash-toyota",
        "Sales flash — Lakeside Toyota — month to date November 21, 2026",
        "store",
        TOYOTA,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Toyota sales flash, month to date as of November 21, 2026 (sample). Posted for Toyota staff.

Month to date the store has retailed 55 new units and 31 used units. The month-end new-car objective is 170. This flash does not include gross or net profit.

Aged new units over 90 days: one GR86 and one Tundra hybrid. Monday desk meeting will address both.
""",
    ),
    _doc(
        "store-sales-flash-ford",
        "Sales flash — Lakeside Ford — month to date November 21, 2026",
        "store",
        FORD,
        ANY,
        ALL_STAFF,
        "internal",
        """
Lakeside Ford sales flash, month to date as of November 21, 2026 (sample). Posted for Ford staff.

Month to date the store has retailed 38 new units and 18 used units. The month-end new-car objective is 125. This flash does not include gross or net profit.

Two F-150s over 90 days are flagged for a desk review. A weekend service clinic is scheduled for December 5; sales should not promise a clinic discount on a vehicle purchase.
""",
    ),
    _doc(
        "store-inventory-honda",
        "Inventory aging — Lakeside Honda — November 2026",
        "store",
        HONDA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Honda inventory aging as of November 21, 2026 (sample). For the Honda GM, the CFO, and the Controller.

New inventory: 164 units, 58 days supply. Used inventory: 71 units, 41 days supply. Units over 90 days: 6 new and 8 used, with a combined wholesale exposure of $214,000 above MMR on the used side after pack.

Floor-plan interest for October was $21,400. This file is not posted on the sales tower.
""",
    ),
    _doc(
        "store-inventory-toyota",
        "Inventory aging — Lakeside Toyota — November 2026",
        "store",
        TOYOTA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Toyota inventory aging as of November 21, 2026 (sample). For the Toyota GM, the CFO, and the Controller.

New inventory: 188 units, 54 days supply. Used inventory: 80 units, 38 days supply. Units over 90 days: 4 new and 6 used. Floor-plan interest for October was $24,900.

The Tundra hybrid over 90 days carries a $3,400 holdback still on the books; do not advertise a price that ignores that without the GM's sign-off.
""",
    ),
    _doc(
        "store-advertising-honda",
        "Advertising spend — Lakeside Honda — October 2026",
        "store",
        HONDA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Honda advertising spend, October 2026 (sample). For the Honda GM, the CFO, and the Controller.

Total advertising is $58,400: digital $31,000, radio $12,400, direct mail $8,200, and events $6,800. Cost per retail unit on a simple October basis is $228. The Honda Civic weekend event on October 18 cost $4,100 and was associated with 14 credited units in the marketing log, which is a tracking estimate, not a proven causal number.

This file is not shared with service advisors or with other stores.
""",
    ),
    _doc(
        "store-marketing-toyota",
        "Marketing calendar — Lakeside Toyota — Q4 2026",
        "store",
        TOYOTA,
        ANY,
        FINANCE_READERS,
        "confidential",
        """
Lakeside Toyota marketing calendar, fourth quarter 2026 (sample). For the Toyota GM, the CFO, and the Controller.

November: service clinic November 14 (completed) and a month-end digital push November 28–30 with a planned spend of $9,500. December: year-end sales event December 26–31 with a planned spend of $22,000, plus a hybrid battery campaign mailer in mid-December at $3,200.

Planned Q4 Toyota advertising is $171,000, which is $11,000 under the quarterly budget. This calendar is not a public event flyer.
""",
    ),
]


assert len(DOCUMENTS) >= 30, len(DOCUMENTS)
assert len({d.id for d in DOCUMENTS}) == len(DOCUMENTS), "duplicate document ids"
