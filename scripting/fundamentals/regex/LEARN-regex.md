
# 1. Regex Parsing        

This sub project demonstrates use of Python’s built-in **`re` (Regular Expressions)** module to parse structured text data to meaningful fields.

---

## Dataset

The sample dataset (`data.txt`) is from [Corey Schafer’s Python Regex tutorial](https://github.com/CoreyMSchafer/code_snippets/tree/c6969cfffca4c0de836453571bb4831451b76a75/Regular-Expressions/data.txt).  
It contains blocks of records with the format:

```bash
Name Surname
Phone Number
Street Address, City State ZIP
Email
```
eg
```bash
Charles Harris
800-555-5669
969 High St., Atlantis VA 34075
charlesharris@bogusemail.com
```
## What this project does

1. **Reads the raw data** from `data.txt`.
2. **Groups each record** (name → phone → address → email) into a single match using regex.
3. **Splits the record** into individual lines for easier handling.
4. **Parses the address line** further into:
   - Street  
   - City  
   - State  
   - ZIP Code
5. **Prints structured output** for each record.
## Concepts / Topics Covered

- **Regex basics**  
  - Anchors: `^`, `$`  
  - Quantifiers: `*`, `+`, `?`  
  - Groups: `(...)`  
  - Non-greedy matching with `.*?`  
  - Multiline flag `re.MULTILINE`  

- **Data extraction**  
  - Using `re.compile()` and `finditer()`  
  - Capturing groups for subfields  
  - Splitting records into structured Python variables  

- **Practical parsing**  
  - Turning unstructured text into structured data  
  - Extracting complex address components with regex  

---

## Example Output

output blocks eill be in the format

```bash
names: Name Surname
phone: Phone Number
address:
    street: Street Address
    city: City 
    state: State
    zip: ZIP
email: Email Address
```
eg

```bash
names:  Charles Harris
phone:  800-555-5669
address: 
        street:  969 High St.
        city:  Atlantis
        state:  VA
        zip:  34075
email:  charlesharris@bogusemail.com
```


[back to top](#1-regex-parsing)

[HOME](/README.md)
