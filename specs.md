A Python program with a minimal UI is needed with the following specifications.

# UI input: _parts list_

There is a text file, a sample of which is attached.

The text file is called _parts list_. The user uploads the text file through the minimal UI.

## Column separator for _parts list_

The columns of the _parts list_ text file are separated by the _tab_ character. The _space_ character separates words inside the same _column_.

# UI input: _price table_

The UI will let user enter a price table.

The rows of the price table would contain three columns:

* 1st column: _type_ of part
* 2nd column: _color_ of part
* 3rd column: _price_ of part

The UI will have proper column headers to be user-friendly.

# Two UI outputs: _intermediate table_ and _final table_

The UI would display two tables:

* The _intermediate_ table.
* The _final_ table.

The user would be shown the _intermediate_ table. After user modification and approval, the _final_ table is displayed.

# UI output: _intermediate table_

## Rows of _intermediate table_

From _parts list_, only rows whose first column includes `ADIN` letters are needed. The other rows are discarded.

## Columns of _intermediate table_

The columns of _intermediate table_ are mostly extracted from the _parts list_.

Only extract the rows from _parts list_ whose first column includes `ADIN` letters.

The 1st to 7th columns are directly extracted from _parts list_ text file.

The 8th column is computed by a _formula_ described by the next section.

The columns of the _intermediate table_ are as follows:

* 1st column: part _type_
   * Extract from column 2 of _parts list_
* 2nd column: part `L`
   * Extract from column 4 of _parts list_
* 3rd column: part `P`
   * Extract from column 5 of _parts list_
* 4th column: part `H`
   * Extract from column 6 of _parts list_
* 5th column: part _door model_
   * Extract from column 11 of _parts list_
* 6th column: part _color_
   * Extract from column 13 of _parts list_
* 7th column: part _color code_
   * Extract from column 14 of _parts list_
* 8th column: part _formula_ output
   * Compute by a _formula_ described by the next section.

The 8th column of the _intermediate table_ is the output of a _formula_. The next section describes the _formula_ according to each part _type_.

## The _formula_ for 8th column of _intermediate table_

### Units of formula computation

The input unit of `L`, `P`, and `H` on the _parts list_ are millimeter. The unit should be converted to meter before the formula computations. It means, the `L`, `P`, and `H` values should be divided by `1000` beforehand.

### Formula computation

To produce the 8th column of the _intermediate table_, the program will compute the following formula corresponding to each row.

For each focused row, apply a formula as below. Note that the _type_ text letters are case insensitive.

* Type starting with `Base` letters:
   * Formula is `P*(H/0.72)*L`
* Type starting with `Tall` letters:
   * Formula is `P*(H/0.72)*L`
* Type starting with `Wall` letters, then:
   * Formula is `(Factor_H + Factor_P) * L`
   * `Factor_H` is:
       * If `H<=0.40`, then `Factor_H` is `0.25`
       * If `0.40<H<=0.50`, then `Factor_H` is `0.30`
       * If `0.50<H<=0.60`, then `Factor_H` is `0.35`
       * If `0.60<H<=0.70`, then `Factor_H` is `0.40`
       * If `0.70<H`, then `Factor_H` is `0.40+(H-0.70)`
   * `Factor_P` is:
       * `Factor_P` is `(P-0.30)/2`
           * If `P<0.30`, then `Factor_P` is negative
           * If `0.30<P`, then `Factor_P` is positive
           * If `P==0.30`, then `Factor_P` is zero
* Type starting with `NAMA U` letters:
   * Formula is `(P+L+0.08)*H`
* Type starting with `NAMA L` letters:
   * Formula is `(P+L)*H`
* Type starting with `NAMA 16` or `NAMA16` letters:
   * Formula is `H*P`
* Type starting with `NAMA 32` letters:
   * Formula is `H*P*2`
* Type starting with `NAMA CNC` letters:
   * Formula is `L*P*2`
* Type starting with `NAMA ver 16` letters:
   * Formula is `L*P`
* Type starting with `NAMA ver 32` letters:
   * Formula is `L*P*2`
* Type starting with `NAMA hor with light` letters:
   * Formula is `L*P + L * Factor_light`
       * `Factor_light` is `550`
* Type starting with `NAMA ver with light` letters:
   * Formula is `H*P + H * Factor_light`
       * `Factor_light` is `550`
* Type starting with `Open shelf` letters:
   * Formula is `(L*P)*2+(H*P)*2+(L*H)`
* Type starting with `Shelf` letters:
   * Formula is `(L*P)*2+(H*P)*2+(L*H)*2 + Factor_farsi`
   * Where `Factor_farsi` is `2*(2*P+L+H)`
* Type starting with `SAFHE 60` letters:
   * Formula is `L*Factor_price`
       * Where `Factor_price` will be looked up by _type_ and _color_ from price table.
* Type starting with `Safhe 65` letters:
   * Formula is `L*Factor_price`
       * Where `Factor_price` will be looked up by _type_ and _color_ from price table.
* Type starting with `Safhe 75` letters:
   * Formula is `L*Factor_price`
       * Where `Factor_price` will be looked up by _type_ and _color_ from price table.
* Type starting with `Safhe 90` letters:
   * Formula is `L*Factor_price`
       * Where `Factor_price` will be looked up by _type_ and _color_ from price table.
* Type starting with `Safhe 100` letters:
   * Formula is `L*Factor_price`
       * Where `Factor_price` will be looked up by _type_ and _color_ from price table.
* Type starting with `Safhe 120` letters:
   * Formula is `L*Factor_price`
       * Where `Factor_price` will be looked up by _type_ and _color_ from price table.
* Type starting with `Ward` letters:
   * Formula is `L * H * Factor_P`
   * `Factor_P` is:
      * If `P<=0.30`, then `0.45`
      * If `0.30<P<=0.40`, then `0.5`
      * If `0.40<P<=0.50`, then `0.55`
      * If `0.50<P<=0.60`, then `0.6`
      * If `0.60<P<=0.70`, then `0.65`
      * If `0.70<P<=0.80`, then `0.7`
      * If `0.80<P<=0.90`, then `0.75`
      * If `0.90<P<=0.100`, then `0.8`
      * If `0.100<P<=0.110`, then `0.85`
      * If `0.110<P`, then `0.9`
* Type starting with `Kesho 1` letters:
   * Formula is `L+P+H`
* Type starting with `Kesho 2` letters:
   * Formula is `L+P+H`
* Type starting with `Kesho 3` letters:
   * Formula is `L+P+H`
* Type starting with `Kesho 4` letters:
   * Formula is `L+P+H`
* Type starting with `Tabaghe 1` letters:
   * Formula is `L+P+H`
* Type starting with `Tabaghe 2` letters:
   * Formula is `L+P+H`
* Type starting with `Tabaghe 3` letters:
   * Formula is `L+P+H`
* Type starting with `Tabaghe 4` letters:
   * Formula is `L+P+H`
* Type starting with `Tabaghe 5` letters:
   * Formula is `L+P+H`
* Type starting with `Tabaghe 6` letters:
   * Formula is `L+P+H`

## Display _intermediate table_

Display the _intermediate table_ in a user-friendly way.

The UI should let the user modify the cell values of the  _intermediate table_ if needs be.

# UI output: _final table_

The _final table_ will be specified later. For now, just creation of the _intermediate table_ is enough.
