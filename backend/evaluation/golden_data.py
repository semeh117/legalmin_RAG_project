GOLDEN_DATASET = [
    {
        "question": "What is the employee's annual base salary?",
        "expected_answer": "The employee's annual base salary is $135,000.00, as stated on page 1 of the document.",
        "expected_context": " The Company shall pay the Employee an annualized base salary of $135,000.00 USD"
    },
    {
        "question" : "How many days of Paid Time Off is the employee entitled to per year?",
        "expected_answer": "The employee is entitled to 20 days of Paid Time Off per year, as stated on page 2 of the document.",
        "expected_context": " Twenty (20) days of accrued Paid Time Off per calendar year, in addition to recognized company holidays"

    },
    {
        "question" : "What is the maximum severance the employee can receive if terminated without cause?",
        "expected_answer": "The employee receives one month of base salary for each completed year of service, up to a maximum of six months, contingent upon signing a standard release of claims.",
        "expected_context": "up to a maximum of six (6) months, contingent upon the execution of a standard release of claims"
    },
    {
        "question":"How often does the employee need to visit the corporate office?",
        "expected_answer":"The employee is required to visit the corporate office up to 3 days per month.",
        "expected_context":"the requirement to visit the corporate office in Tech City, TX, up to three (3) days per month for strategic planning and team-building sessions",
    },
    {
        "question":"Can the company end the employment relationship without giving a reason?",
        "expected_answer":"yes, the company can terminate the employment relationship at any time without cause,and with or without notice.",
        "expected_context":" either the Company or the Employee may terminate theemployment relationship at any time, with or without cause, and with or without advance notice."
    },
    {  
        "question":"Who owns the code and data pipelines the employee builds during their employment?",
        "expected_answer" :"The company owns all code and data pipelines built by the employee during their employment.",
        "expected_context":"Any software, algorithms, code, data pipelines, processes, or other intellectual property developed, created, or improved by the Employee during the term of employment, whether during or outside working hours, which relates to the Company's business, shall be the sole and exclusive property of the Company."
    },
    {
        "question":"Is the employee entitled to a bonus, and is it guaranteed?",
        "expected_answer":"The employee is eligible for an annual performance bonus of up to 15% of their base salary, but it is not guaranteed ",
        "expected_context":"The Employee shall be eligible for an annual discretionary performance bonus of up to 15% of their base salary. The bonus will be based on the achievement of individual and corporate performance"
    },
    {
        "question":"what is the total potential annual compensation including base salary and maximum bonus ?",
        "expected_answer" :"it's the sum of the base salary and the maximum bonus which is $135,000.00 + (15% of $135,000.00) = $155,250.00",
        "expected_context": "The Company shall pay the Employee an annualized base salary of $135,000.00 USD. The Employee shall be eligible for an annual discretionary performance bonus of up to 15% of their base salary."   
    },
    {
        "question" :"If the employee is terminated without cause after 3 years, how much severance do they receive?",
        "expected_answer":"the severance is caclculated as [3 months × ($135,000 ÷ 12) = $33,750 ]",
        "expected_context":"the Employee shall be entitled to severance pay equal to one (1) month of base salary for each completed year of service, up to a maximum of six(6) months, contingent upon the execution of a standard release of claims."
    },
    {
        "question":"What is the employee's non-compete obligation after leaving the company?",
        "expected_answer":"The document does not contain a non-compete clause.",
        "expected_context":""
    }
]