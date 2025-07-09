There is an specification for a G-code generation software tool. It's used for manufacturing wood doors for kitchen cabinets.

# Workflow

* The `KitchenDraw` software:
   * Has the sub-assemblies of the cabinet.
   * Has the parts of the cabinet.
   * Exports the cutting list as CSV file.
* The `CutList Plus fx` software:
   * Imports the CSV file.
   * Creates the layout sheets according to predefined sheets.
   * Exports each sheet as a separte DXF file.
* A human:
   * To separate door DXF files from other parts DXF files.
* DXF file is modified:
   * By adding offsets inside the door.
* ArtCAM takes the DXF file.
   * Create tool paths.
* ArtCAM generates G-code.
