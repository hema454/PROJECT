# Structured Extraction Report

**Model:** llama3.1:8b
**Total runs:** 50
**Success (first try):** 24
**Recovered (after retry):** 22
**Failed (reported cleanly):** 4

## Failure modes exercised across all 50 runs

- Markdown fences around JSON: ✅
- Prose before the JSON: ✅
- Trailing comma: ❌ never observed
- Truncated mid-object: ❌ never observed

## Per-run detail (diagnostics shown even for successes)

- **Run 1** — recovered: {'name': 'Priya Nair', 'email': 'priya.nair@zentra.com', 'company': 'Zentra Labs', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value=' [email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 2** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 3** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworksinc.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 4** — recovered: {'name': 'Karthik', 'email': 'karthik.solstice@gmail.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 5** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 6** — success: {'name': 'Priya Nair', 'email': 'priya.nair@zentra.labs', 'company': 'Zentra Labs', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 7** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 8** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworksinc.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 9** — recovered: {'name': 'Karthik', 'email': 'karthik.sriv@gmail.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 10** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 11** — failed: Failed after retry — second: 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='p [email protected]', input_type=str]
- **Run 12** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 13** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworks.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 14** — recovered: {'name': 'Karthik', 'email': 'karthik@solsticesystems.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
- **Run 15** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 16** — success: {'name': 'Priya Nair', 'email': 'priya.nair@zentra.labs', 'company': 'Zentra Labs', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 17** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 18** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworksinc.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 19** — recovered: {'name': 'Karthik', 'email': 'karthik@solutions-systems.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 20** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 21** — success: {'name': 'Priya Nair', 'email': 'nair.priya@zentralabs.com', 'company': 'Zentra Labs', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 22** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 23** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworksinc.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 24** — recovered: {'name': 'Karthik', 'email': 'karthik.k@gmail.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 25** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 26** — failed: Retry request failed: timed out
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value=' [email protected] ', input_type=str]
- **Run 27** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 28** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworksinc.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 29** — recovered: {'name': 'Karthik', 'email': 'karthik@example.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 30** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 31** — recovered: {'name': 'Priya Nair', 'email': 'priya.nair@zentra.labs', 'company': 'Zentra Labs', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 32** — success: {'name': 'rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 33** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworks.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 34** — recovered: {'name': 'Karthik', 'email': 'karthik.sreedharan@solsticesystems.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 35** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 36** — recovered: {'name': 'Priya Nair', 'email': 'priya.nair@zentra.com', 'company': 'Zentra Labs', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value=' [email protected] ', input_type=str]
  - *cleanup applied:* markdown_fences
- **Run 37** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 38** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworks.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 39** — recovered: {'name': 'Karthik', 'email': 'karthik@example.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 40** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 41** — success: {'name': 'Priya Nair', 'email': 'priya.nair@zentra.labs', 'company': 'Zentra Labs', 'urgent': True}
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 42** — success: {'name': 'Rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 43** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworks.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 44** — recovered: {'name': 'Karthik', 'email': 'karthik@example.com', 'company': 'Solstice Systems', 'urgent': False}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *cleanup applied:* markdown_fences, prose_before_json
- **Run 45** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences
- **Run 46** — failed: Failed after retry — second: 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value=' [email protected] ', input_type=str]
- **Run 47** — success: {'name': 'rohan', 'email': 'rohan.k@outbox.io', 'company': 'Brightline Co.', 'urgent': False}
  - *cleanup applied:* markdown_fences
- **Run 48** — recovered: {'name': 'Aditi Sharma', 'email': 'aditi.sharma@novaworksinc.com', 'company': 'NovaWorks Inc', 'urgent': True}
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
- **Run 49** — failed: Failed after retry — second: 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='', input_type=str]
  - *first-attempt error:* 1 validation error for ExtractedContact
email
  value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='[email protected]', input_type=str]
- **Run 50** — success: {'name': 'Meera Iyer', 'email': 'meera_iyer@quantail.com', 'company': 'Quantail', 'urgent': True}
  - *cleanup applied:* markdown_fences