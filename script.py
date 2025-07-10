import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
from typing import List, Dict, Tuple

class PartsListProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Parts List Processor")
        self.root.geometry("1200x700")
        
        # Data storage
        self.parts_data = []
        self.quantity_table_data = []
        self.summary_table_data = []
        self.cost_table_data = []
        self.deleted_rows = set()  # Track deleted rows
        self.price_table_path = "price_table.csv"
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Create UI elements
        self.create_ui()
        
        # Initialize price table if it doesn't exist
        self.initialize_price_table()
    
    def create_ui(self):
        # File upload section
        upload_frame = ttk.Frame(self.main_frame)
        upload_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(upload_frame, text="Upload Parts List", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(upload_frame, text="Edit Price Table", command=self.edit_price_table).pack(side=tk.LEFT, padx=5)
        
        # Table frame
        self.table_frame = ttk.Frame(self.main_frame)
        self.table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.table_frame.columnconfigure(0, weight=1)
        self.table_frame.rowconfigure(0, weight=1)
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Please upload a parts list file")
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E))
    
    def initialize_price_table(self):
        """Create a default price table CSV if it doesn't exist"""
        if not os.path.exists(self.price_table_path):
            headers = ['Door model', 'Color category', 'Color code', 'Cabinet', 'Wardrobe', 
                      'NAMA', 'Safhe 60', 'Safhe 65', 'Safhe 75', 'Safhe 90', 'Safhe 100', 
                      'Safhe 120', 'Open shelf', 'Shelf', 'Kesho', 'Tabaghe', 'Description']
            
            with open(self.price_table_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                # Add some example rows
                writer.writerow(['MO1', 'TYPE', 'TISAN', '1000', '1200', '800', '500', '550', 
                               '600', '650', '700', '750', '900', '1100', '1300', '1500', 'Example'])
                writer.writerow(['MO10', 'TYPE', 'TISAN', '1100', '1300', '850', '520', '570', 
                               '620', '670', '720', '770', '920', '1150', '1350', '1550', 'Example'])
                writer.writerow(['MO7', 'TYPE', 'TISAN', '1050', '1250', '825', '510', '560', 
                               '610', '660', '710', '760', '910', '1125', '1325', '1525', 'Example'])
    
    def upload_file(self):
        filename = filedialog.askopenfilename(
            title="Select Parts List File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.process_parts_list(filename)
    
    def process_parts_list(self, filename):
        """Process the uploaded parts list file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.parts_data = []
            self.deleted_rows = set()  # Reset deleted rows
            
            for line in lines:
                columns = line.strip().split('\t')
                if len(columns) >= 14 and 'ADIN' in columns[0]:
                    self.parts_data.append(columns)
            
            if self.parts_data:
                self.create_quantity_table()
                self.status_label.config(text=f"Loaded {len(self.parts_data)} ADIN parts")
            else:
                messagebox.showwarning("No Data", "No ADIN parts found in the file")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {str(e)}")
    
    def calculate_formula(self, part_type: str, L: float, P: float, H: float) -> float:
        """Calculate the formula output based on part type"""
        # Convert mm to meters
        L = L / 1000
        P = P / 1000
        H = H / 1000
        
        part_type = part_type.upper()
        
        # Base and Tall
        if part_type.startswith('BASE') or part_type.startswith('TALL'):
            return P * (H / 0.72) * L
        
        # Wall
        elif part_type.startswith('WALL'):
            # Calculate Factor_H
            if H <= 0.40:
                factor_h = 0.25
            elif H <= 0.50:
                factor_h = 0.30
            elif H <= 0.60:
                factor_h = 0.35
            elif H <= 0.70:
                factor_h = 0.40
            else:
                factor_h = 0.40 + (H - 0.70)
            
            # Calculate Factor_P
            factor_p = (P - 0.30) / 2
            
            return (factor_h + factor_p) * L
        
        # NAMA variants
        elif part_type.startswith('NAMA U'):
            return (P + L + 0.08) * H
        elif part_type.startswith('NAMA L'):
            return (P + L) * H
        elif part_type.startswith('NAMA 16') or part_type.startswith('NAMA16'):
            return H * P
        elif part_type.startswith('NAMA 32'):
            return H * P * 2
        elif part_type.startswith('NAMA CNC'):
            return L * P * 2
        elif part_type.startswith('NAMA VER 16'):
            return L * P
        elif part_type.startswith('NAMA VER 32'):
            return L * P * 2
        elif part_type.startswith('NAMA HOR WITH LIGHT'):
            factor_light = 0.55  # 550mm converted to meters
            return L * P + L * factor_light
        elif part_type.startswith('NAMA VER WITH LIGHT'):
            factor_light = 0.55
            return H * P + H * factor_light
        
        # Open shelf and Shelf
        elif part_type.startswith('OPEN SHELF'):
            return (L * P) * 2 + (H * P) * 2 + (L * H)
        elif part_type.startswith('SHELF'):
            factor_farsi = 2 * (2 * P + L + H)
            return (L * P) * 2 + (H * P) * 2 + (L * H) * 2 + factor_farsi
        
        # SAFHE variants
        elif any(part_type.startswith(f'SAFHE {x}') for x in ['60', '65', '75', '90', '100', '120']):
            return L * 1000  # Return in mm for linear measurements
        
        # Ward
        elif part_type.startswith('WARD'):
            if P <= 0.30:
                factor_p = 0.45
            elif P <= 0.40:
                factor_p = 0.50
            elif P <= 0.50:
                factor_p = 0.55
            elif P <= 0.60:
                factor_p = 0.60
            elif P <= 0.70:
                factor_p = 0.65
            elif P <= 0.80:
                factor_p = 0.70
            elif P <= 0.90:
                factor_p = 0.75
            elif P <= 1.00:
                factor_p = 0.80
            elif P <= 1.10:
                factor_p = 0.85
            else:
                factor_p = 0.90
            return L * H * factor_p
        
        # Kesho
        elif part_type.startswith('KESHO'):
            return P * (H / 0.72) * L * 2
        
        # Tabaghe
        elif part_type.startswith('TABAGHE'):
            # Extract number from type
            for i in range(1, 7):
                if f'TABAGHE {i}' in part_type.upper() or f'TABAGHE{i}' in part_type.upper():
                    return L * P * H * i
        
        return 0.0
    
    def create_quantity_table(self):
        """Create and display the quantity table with fixed headers"""
        # Clear existing widgets
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Create container frame for headers and scrollable content
        container_frame = ttk.Frame(self.table_frame)
        container_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container_frame.columnconfigure(0, weight=1)
        container_frame.rowconfigure(1, weight=1)
        
        # Create headers frame (fixed)
        headers_frame = ttk.Frame(container_frame)
        headers_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Create headers
        headers = ["Type", "L (mm)", "P (mm)", "H (mm)", "Door Model", 
                  "Color Category", "Color Code", "Formula Output", "Delete"]
        
        for col, header in enumerate(headers):
            label = ttk.Label(headers_frame, text=header, font=('Arial', 10, 'bold'), relief=tk.RIDGE)
            label.grid(row=0, column=col, padx=1, pady=1, sticky=(tk.W, tk.E))
            if col < 8:
                headers_frame.columnconfigure(col, minsize=120)
            else:
                headers_frame.columnconfigure(col, minsize=70)
        
        # Create scrollable frame for data
        data_container = ttk.Frame(container_frame)
        data_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_container.columnconfigure(0, weight=1)
        data_container.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(data_container, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(data_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(container_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Process data and create table rows
        self.quantity_table_data = []
        self.entry_widgets = []
        
        for row_idx, part in enumerate(self.parts_data):
            try:
                # Extract values
                part_type = part[1].strip()
                L = float(part[3].strip()) if part[3].strip() else 0
                P = float(part[4].strip()) if part[4].strip() else 0
                H = float(part[5].strip()) if part[5].strip() else 0
                door_model = part[10].strip() if len(part) > 10 else ""
                color_category = part[12].strip() if len(part) > 12 else ""
                color_code = part[13].strip() if len(part) > 13 else ""
                
                # Calculate formula
                formula_output = self.calculate_formula(part_type, L, P, H)
                
                # Store data
                row_data = [part_type, L, P, H, door_model, color_category, color_code, formula_output]
                self.quantity_table_data.append(row_data)
                
                # Create entry widgets for editable cells
                row_entries = []
                for col, value in enumerate(row_data):
                    if col < 7:  # All columns except formula output are editable
                        entry = ttk.Entry(scrollable_frame, width=15)
                        entry.insert(0, str(value))
                        entry.grid(row=row_idx, column=col, padx=1, pady=1)
                        # Check if this row was previously deleted
                        if row_idx in self.deleted_rows:
                            entry.config(state='disabled')
                        row_entries.append(entry)
                    else:  # Formula output - display only
                        label = ttk.Label(scrollable_frame, text=f"{value:.4f}")
                        label.grid(row=row_idx, column=col, padx=1, pady=1)
                        row_entries.append(label)
                
                # Delete button
                delete_btn = ttk.Button(scrollable_frame, text="Delete", 
                                      command=lambda r=row_idx: self.delete_row(r))
                delete_btn.grid(row=row_idx, column=8, padx=1, pady=1)
                if row_idx in self.deleted_rows:
                    delete_btn.config(state='disabled')
                row_entries.append(delete_btn)
                
                self.entry_widgets.append(row_entries)
                
            except Exception as e:
                print(f"Error processing row {row_idx}: {e}")
        
        # Configure column widths in scrollable frame to match headers
        for col in range(9):
            if col < 8:
                scrollable_frame.columnconfigure(col, minsize=120)
            else:
                scrollable_frame.columnconfigure(col, minsize=70)
        
        # Pack scrollbars and canvas
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Add buttons
        ttk.Button(self.button_frame, text="Recalculate", command=self.recalculate_formulas).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Approve and Continue", command=self.create_summary_table).pack(side=tk.LEFT, padx=5)
        
        self.status_label.config(text="Quantity table created. You can edit values and click 'Recalculate'.")
    
    def delete_row(self, row_index):
        """Mark row for deletion"""
        if 0 <= row_index < len(self.entry_widgets):
            self.deleted_rows.add(row_index)
            for widget in self.entry_widgets[row_index]:
                if isinstance(widget, (ttk.Entry, ttk.Label)):
                    widget.config(state='disabled')
                elif isinstance(widget, ttk.Button):
                    widget.config(state='disabled')
    
    def recalculate_formulas(self):
        """Recalculate formulas based on current entry values"""
        for row_idx, row_entries in enumerate(self.entry_widgets):
            try:
                # Skip deleted rows
                if row_idx in self.deleted_rows:
                    continue
                
                # Get current values
                part_type = row_entries[0].get()
                L = float(row_entries[1].get())
                P = float(row_entries[2].get())
                H = float(row_entries[3].get())
                
                # Recalculate formula
                formula_output = self.calculate_formula(part_type, L, P, H)
                
                # Update formula output label
                row_entries[7].config(text=f"{formula_output:.4f}")
                
                # Update stored data
                self.quantity_table_data[row_idx] = [
                    part_type,
                    L, P, H,
                    row_entries[4].get(),
                    row_entries[5].get(),
                    row_entries[6].get(),
                    formula_output
                ]
                
            except Exception as e:
                print(f"Error recalculating row {row_idx}: {e}")
        
        self.status_label.config(text="Formulas recalculated")
    
    def create_summary_table(self):
        """Create and display the summary table with fixed headers"""
        # First, update quantity table data with current values
        self.recalculate_formulas()
        
        # Group data by type, door model, color category, and color code
        summary_dict = {}
        
        for row_idx, row_data in enumerate(self.quantity_table_data):
            # Skip deleted rows
            if row_idx in self.deleted_rows:
                continue
            
            part_type = self.normalize_type(row_data[0])
            door_model = row_data[4]
            color_category = row_data[5]
            color_code = row_data[6]
            formula_output = row_data[7]
            
            key = (part_type, door_model, color_category, color_code)
            
            if key in summary_dict:
                summary_dict[key] += formula_output
            else:
                summary_dict[key] = formula_output
        
        # Clear existing widgets
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Create container frame for headers and scrollable content
        container_frame = ttk.Frame(self.table_frame)
        container_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container_frame.columnconfigure(0, weight=1)
        container_frame.rowconfigure(1, weight=1)
        
        # Create headers frame (fixed)
        headers_frame = ttk.Frame(container_frame)
        headers_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Create headers
        headers = ["Type", "Door Model", "Color Category", "Color Code", "Total Formula Output"]
        
        for col, header in enumerate(headers):
            label = ttk.Label(headers_frame, text=header, font=('Arial', 10, 'bold'), relief=tk.RIDGE)
            label.grid(row=0, column=col, padx=1, pady=1, sticky=(tk.W, tk.E))
            headers_frame.columnconfigure(col, minsize=150)
        
        # Create scrollable frame for data
        data_container = ttk.Frame(container_frame)
        data_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_container.columnconfigure(0, weight=1)
        data_container.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(data_container, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(data_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(container_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Create summary rows
        self.summary_table_data = []
        
        for row_idx, (key, total) in enumerate(sorted(summary_dict.items())):
            part_type, door_model, color_category, color_code = key
            
            row_data = [part_type, door_model, color_category, color_code, total]
            self.summary_table_data.append(row_data)
            
            for col, value in enumerate(row_data):
                if col == 4:  # Formula output
                    text = f"{value:.4f}"
                else:
                    text = str(value)
                label = ttk.Label(scrollable_frame, text=text)
                label.grid(row=row_idx, column=col, padx=1, pady=1, sticky=tk.W)
                scrollable_frame.columnconfigure(col, minsize=150)
        
        # Pack scrollbars and canvas
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Add button
        ttk.Button(self.button_frame, text="Approve and Calculate Costs", 
                  command=self.create_cost_table).pack(side=tk.LEFT, padx=5)
        
        self.status_label.config(text=f"Summary table created with {len(self.summary_table_data)} rows")
    
    def normalize_type(self, part_type: str) -> str:
        """Normalize part type for grouping"""
        part_type = part_type.upper()
        
        type_groups = {
            'BASE': 'Base',
            'TALL': 'Tall',
            'WALL': 'Wall',
            'NAMA': 'NAMA',
            'SAFHE 60': 'Safhe 60',
            'SAFHE 65': 'Safhe 65',
            'SAFHE 75': 'Safhe 75',
            'SAFHE 90': 'Safhe 90',
            'SAFHE 100': 'Safhe 100',
            'SAFHE 120': 'Safhe 120',
            'WARD': 'Ward',
            'OPEN SHELF': 'Open shelf',
            'SHELF': 'Shelf',
            'KESHO': 'Kesho',
            'TABAGHE': 'Tabaghe'
        }
        
        for prefix, normalized in type_groups.items():
            if part_type.startswith(prefix):
                return normalized
        
        return part_type
    
    def create_cost_table(self):
        """Create and display the cost table with fixed headers"""
        # Load price table
        price_data = self.load_price_table()
        
        if not price_data:
            messagebox.showerror("Error", "Price table not found or empty. Please edit the price table first.")
            return
        
        # Clear existing widgets
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Create container frame for headers and scrollable content
        container_frame = ttk.Frame(self.table_frame)
        container_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container_frame.columnconfigure(0, weight=1)
        container_frame.rowconfigure(1, weight=1)
        
        # Create headers frame (fixed)
        headers_frame = ttk.Frame(container_frame)
        headers_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Create headers
        headers = ["Type", "Door Model", "Color Category", "Color Code", 
                  "Total Formula Output", "Unit Price", "Total Price"]
        
        for col, header in enumerate(headers):
            label = ttk.Label(headers_frame, text=header, font=('Arial', 10, 'bold'), relief=tk.RIDGE)
            label.grid(row=0, column=col, padx=1, pady=1, sticky=(tk.W, tk.E))
            headers_frame.columnconfigure(col, minsize=130)
        
        # Create scrollable frame for data
        data_container = ttk.Frame(container_frame)
        data_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_container.columnconfigure(0, weight=1)
        data_container.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(data_container, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(data_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(container_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Create cost rows
        self.cost_table_data = []
        total_cost = 0
        
        for row_idx, row_data in enumerate(self.summary_table_data):
            part_type = row_data[0]
            door_model = row_data[1]
            color_category = row_data[2]
            color_code = row_data[3]
            formula_output = row_data[4]
            
            # Get unit price
            unit_price = self.get_unit_price(part_type, door_model, color_category, 
                                            color_code, price_data)
            
            # Calculate total price
            total_price = formula_output * unit_price
            total_cost += total_price
            
            # Store data
            cost_row = row_data + [unit_price, total_price]
            self.cost_table_data.append(cost_row)
            
            # Display row
            for col, value in enumerate(cost_row):
                if col in [4, 5, 6]:  # Numeric columns
                    text = f"{value:.2f}"
                else:
                    text = str(value)
                label = ttk.Label(scrollable_frame, text=text)
                label.grid(row=row_idx, column=col, padx=1, pady=1, sticky=tk.W)
                scrollable_frame.columnconfigure(col, minsize=130)
        
        # Add total row
        ttk.Label(scrollable_frame, text="TOTAL", font=('Arial', 10, 'bold')).grid(
            row=len(self.cost_table_data), column=5, padx=1, pady=5, sticky=tk.E)
        ttk.Label(scrollable_frame, text=f"{total_cost:.2f}", font=('Arial', 10, 'bold')).grid(
            row=len(self.cost_table_data), column=6, padx=1, pady=5, sticky=tk.W)
        
        # Pack scrollbars and canvas
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Add buttons
        ttk.Button(self.button_frame, text="Export to CSV", 
                  command=self.export_cost_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="New Analysis", 
                  command=self.reset_analysis).pack(side=tk.LEFT, padx=5)
        
        self.status_label.config(text=f"Cost table created. Total cost: {total_cost:.2f}")
    
    def load_price_table(self) -> List[Dict]:
        """Load price table from CSV"""
        price_data = []
        
        try:
            with open(self.price_table_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    price_data.append(row)
        except Exception as e:
            print(f"Error loading price table: {e}")
        
        return price_data
    
    def get_unit_price(self, part_type: str, door_model: str, color_category: str, 
                      color_code: str, price_data: List[Dict]) -> float:
        """Get unit price from price table"""
        # Map part types to price table columns
        type_to_column = {
            'Base': 'Cabinet',
            'Tall': 'Cabinet',
            'Wall': 'Cabinet',
            'Ward': 'Wardrobe',
            'NAMA': 'NAMA',
            'Safhe 60': 'Safhe 60',
            'Safhe 65': 'Safhe 65',
            'Safhe 75': 'Safhe 75',
            'Safhe 90': 'Safhe 90',
            'Safhe 100': 'Safhe 100',
            'Safhe 120': 'Safhe 120',
            'Open shelf': 'Open shelf',
            'Shelf': 'Shelf',
            'Kesho': 'Kesho',
            'Tabaghe': 'Tabaghe'
        }
        
        price_column = type_to_column.get(part_type, '')
        
        if not price_column:
            return 0.0
        
        # Find matching row in price table
        for row in price_data:
            if (row.get('Door model', '').upper() == door_model.upper() and
                row.get('Color category', '').upper() == color_category.upper() and
                row.get('Color code', '').upper() == color_code.upper()):
                
                try:
                    return float(row.get(price_column, 0))
                except ValueError:
                    return 0.0
        
        return 0.0
    
    def export_cost_table(self):
        """Export cost table to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write headers
                    headers = ["Type", "Door Model", "Color Category", "Color Code", 
                             "Total Formula Output", "Unit Price", "Total Price"]
                    writer.writerow(headers)
                    
                    # Write data
                    for row in self.cost_table_data:
                        writer.writerow(row)
                    
                    # Write total
                    total = sum(row[6] for row in self.cost_table_data)
                    writer.writerow(["", "", "", "", "", "TOTAL", total])
                
                messagebox.showinfo("Success", f"Cost table exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting file: {str(e)}")
    
    def edit_price_table(self):
        """Open price table editor"""
        PriceTableEditor(self.root, self.price_table_path)
    
    def reset_analysis(self):
        """Reset for new analysis"""
        # Clear data
        self.parts_data = []
        self.quantity_table_data = []
        self.summary_table_data = []
        self.cost_table_data = []
        self.deleted_rows = set()
        
        # Clear widgets
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        self.status_label.config(text="Please upload a parts list file")


class PriceTableEditor:
    def __init__(self, parent, price_table_path):
        self.price_table_path = price_table_path
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title("Price Table Editor")
        self.window.geometry("1000x600")
        
        # Create UI
        self.create_ui()
        
        # Load existing data
        self.load_data()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create treeview
        self.tree = ttk.Treeview(main_frame, height=20)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Row", command=self.add_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Row", command=self.delete_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        """Load price table data"""
        try:
            with open(self.price_table_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                
                # Configure columns
                self.tree['columns'] = headers
                self.tree['show'] = 'tree headings'
                
                # Set column headings
                for col in headers:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, width=100)
                
                # Load data
                for row in reader:
                    self.tree.insert('', 'end', values=row)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error loading price table: {str(e)}")
    
    def add_row(self):
        """Add new row"""
        # Create input dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Add New Row")
        dialog.geometry("400x500")
        
        entries = []
        columns = self.tree['columns']
        
        for i, col in enumerate(columns):
            ttk.Label(dialog, text=col).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
        
        def save_row():
            values = [entry.get() for entry in entries]
            self.tree.insert('', 'end', values=values)
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_row).grid(row=len(columns), column=0, columnspan=2, pady=10)
    
    def delete_row(self):
        """Delete selected row"""
        selected = self.tree.selection()
        if selected:
            for item in selected:
                self.tree.delete(item)
    
    def save_data(self):
        """Save data to CSV"""
        try:
            with open(self.price_table_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = list(self.tree['columns'])
                writer.writerow(headers)
                
                # Write data
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Success", "Price table saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving price table: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PartsListProcessor(root)
    root.mainloop()
