# Processing parts list

I have a text file as attached. The text file is called _parts list_. I need a Python program with a minimal UI to process the text file as follows.

# UI output

The UI would display two tables:

* The first table that is an intermediate table.
* The second table that is a final table.

The user would be shown the first table. After user modification and approval, the final table is shown.

# Needed rows

Only rows whose first column includes `ADIN` letters are needed. The other rows are discarded.

# First table

To produce the first table, the program will:

* Focus on the rows whose first column includes `ADIN` letters.
* Extract the second column would be the _type_ of part.
* Extract the third column would be discarded. It's not needed.
* Extract the fourth column would be `L`.
* Extract the fifth column would be `P`.
* Extract the sixth column would be `H`.

For each focused row, apply a formula as below.


