# Skill development and Test Automation Project

## Overview

In this project you'll develop a new skill to enhance an existing open-source ERP system, focusing on API and UI test automation.

## Guidelines

1. Choose an ERP web application to enhance. The system must have rich UI and well as **free** API. It's highly recommended that the app can be launched locally on your machine. Below you'll find a list of some open source ERP systems that you can consider.

2. Think about a new skill to add to the system with **clear bussiness value**. The skill will be built as a separated project (separated GitHub repository) and interract with your chosen ERP system using its API. Your skill must include an API at the minimum, but UI is highly recommended. Examples of skills:
   - User can parse documents using AI
   - User can create reports that are not available in the base system using a text prompt
   - User can get insights about the data stored in the system using AI
   - User can integrate the system with a third-party service (e.g., send SMS notifications using Twilio)

3. Develop your skill using best practices taught in the class (working with branches, modular API structure using MVC, HTTP error handling, tests written in POM structure, etc...).

4. Write **automated tests** for your skill. You must provide and follow a clear test plan - what to test (including details test cases) , how to test (including details strategy), success criteria, etc.... The tests must include:
 - Testing your skill app only (mock the base ERP system).
 - Testing the interaction between your skill and the base ERP system with both API and UI tests.

5. Configure a **CI pipeline** in GitHub Actions that will:
 - Test your skill app on every Pull request.
 - Report test results in a clear way (Codecov, Allure, any other tool of your choice).

## Notes

You must make sure your project is **unique** and different from other students' projects.
Please make sure no other student is working on the same combination of:

    - Base ERP choice + a specific business problem/solution
    - A distinct skill/extension scope (API + UI)
    - Different user flows and API endpoints

## Bonus

Collaborate with another student to use her skill in your project. For example, if a student created a skill to parse documents using AI, you can use that skill in your project to create reports based on the parsed documents.

## Presentation  

- Prepare **15 minutes** presentation with **slides** and **live demo**.
- Your slides must have:
    - Short presentation of yourself.
    - Short description of your chosed base ERP system and your skill with emphasis on the bussiness value.
    - Testing overview in higher level - what tested, the strategy, success criteria.
- You must show a **live demo** of your working skill, as well as test execution during the presentation.
- You must show some code snippets of your tests, explaining the design and implementation choices you made.
- Make sure you can confidently answer ANY question regarding your code, decisions. 
- Presenting in English - **bonus**.
- A very short teaser video to communicate Problem → Solution → Impact before the demo - **bonus**.


# Appx - Self-hosted ERP systems

Ideas for self-hosted ERP systems:

- **ERPNext** - https://github.com/frappe/erpnext
- **Dolibarr** - https://github.com/Dolibarr/dolibarr
- **iDempiere** - https://github.com/idempiere/idempiere-docker
- **Metasfresh** - https://github.com/metasfresh/metasfresh



# Good Luck