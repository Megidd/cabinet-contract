import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import re

class PartsListProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Parts List Processor")
        self.root.geometry("1200x900")
        
        # Data storage
        self.parts_data = None
        self.price_table = []
        self.quantity_df = None
        self.summary_df = None
        self.cost_df = None
        self.current_view = "quantity"  # Track current table view
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # File upload section
        upload_frame = ttk.LabelFrame(main_frame, text="Upload Parts List", padding="5")
        upload_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.file_label = ttk.Label(upload_frame, text="No file selected")
        self.file_label.grid(row=0, column=0, padx=5)
        
        ttk.Button(upload_frame, text="Browse", command=self.browse_file).grid(row=0, column=1, padx=5)
        ttk.Button(upload_frame, text="Process File", command=self.process_file).grid(row=0, column=2, padx=5)
        
        # Table display section
        table_frame = ttk.LabelFrame(main_frame, text="Table Display", padding="5")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)
        
        # Table title label
        self.table_title = ttk.Label(table_frame, text="Quantity Table", font=('TkDefaultFont', 12, 'bold'))
        self.table_title.grid(row=0, column=0, pady=5)
        
        # Create Treeview for tables
        self.tree = ttk.Treeview(table_frame, show='headings')
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Edit functionality
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Workflow control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, pady=10)
        
        self.approve_button = ttk.Button(control_frame, text="Approve & Next", command=self.approve_and_next)
        self.approve_button.grid(row=0, column=0, padx=5)
        self.approve_button.config(state='disabled')
        
        self.back_button = ttk.Button(control_frame, text="Back", command=self.go_back)
        self.back_button.grid(row=0, column=1, padx=5)
        self.back_button.config(state='disabled')
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Parts List File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_label.config(text=filename.split('/')[-1])
            self.filename = filename
    
    def normalize_type_for_summary(self, type_text):
        """Normalize type text for summary grouping"""
        type_upper = type_text.upper()
        
        # Define type prefixes for grouping
        type_groups = [
            'BASE', 'TALL', 'WALL', 'NAMA', 'SAFHE 60', 'SAFHE 65', 
            'SAFHE 75', 'SAFHE 90', 'SAFHE 100', 'SAFHE 120',
            'WARD', 'OPEN SHELF', 'SHELF', 'KESHO', 'TABAGHE'
        ]
        
        for prefix in type_groups:
            if type_upper.startswith(prefix):
                return prefix
        
        return type_text  # Return original if no match
    
    def process_file(self):
        if not hasattr(self, 'filename'):
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            # Read the file with tab separator
            with open(self.filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Process lines
            quantity_data = []
            
            for line in lines:
                columns = line.strip().split('\t')
                
                # Check if first column contains 'ADIN'
                if len(columns) >= 14 and 'ADIN' in columns[0]:
                    try:
                        # Extract required columns
                        part_type = columns[1] if len(columns) > 1 else ""
                        # Convert mm to meters
                        L = float(columns[3]) / 1000 if len(columns) > 3 and columns[3] else 0
                        P = float(columns[4]) / 1000 if len(columns) > 4 and columns[4] else 0
                        H = float(columns[5]) / 1000 if len(columns) > 5 and columns[5] else 0
                        door_model = columns[10] if len(columns) > 10 else ""
                        color_category = columns[12] if len(columns) > 12 else ""
                        color_code = columns[13] if len(columns) > 13 else ""
                        
                        # Calculate formula output
                        formula_output = self.calculate_formula(part_type, L, P, H)
                        
                        quantity_data.append({
                            'Type': part_type,
                            'L': L,
                            'P': P,
                            'H': H,
                            'Door Model': door_model,
                            'Color Category': color_category,
                            'Color Code': color_code,
                            'Formula Output': formula_output
                        })
                    except (ValueError, IndexError) as e:
                        continue
            
            self.quantity_df = pd.DataFrame(quantity_data)
            self.current_view = "quantity"
            self.display_quantity_table()
            self.approve_button.config(state='normal')
            
            self.status_label.config(text=f"Processed {len(quantity_data)} ADIN entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {str(e)}")
    
    def calculate_formula(self, part_type, L, P, H):
        """Calculate formula based on part type (L, P, H are already in meters)"""
        part_type_upper = part_type.upper()
        
        # Base and Tall types
        if part_type_upper.startswith('BASE') or part_type_upper.startswith('TALL'):
            return P * (H / 0.72) * L
        
        # Wall types
        elif part_type_upper.startswith('WALL'):
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
        
        # NAMA U types
        elif part_type_upper.startswith('NAMA U'):
            return (P + L + 0.08) * H
        
        # NAMA L types
        elif part_type_upper.startswith('NAMA L'):
            return (P + L) * H
        
        # NAMA 16 or NAMA16 types
        elif part_type_upper.startswith('NAMA 16') or part_type_upper.startswith('NAMA16'):
            return H * P
        
        # NAMA 32 types
        elif part_type_upper.startswith('NAMA 32'):
            return H * P * 2
        
        # NAMA CNC types
        elif part_type_upper.startswith('NAMA CNC'):
            return L * P * 2
        
        # NAMA ver 16 types
        elif part_type_upper.startswith('NAMA VER 16'):
            return L * P
        
        # NAMA ver 32 types
        elif part_type_upper.startswith('NAMA VER 32'):
            return L * P * 2
        
        # NAMA hor with light types
        elif part_type_upper.startswith('NAMA HOR WITH LIGHT'):
            factor_light = 550
            return L * P + L * factor_light
        
        # NAMA ver with light types
        elif part_type_upper.startswith('NAMA VER WITH LIGHT'):
            factor_light = 550
            return H * P + H * factor_light
        
        # Open shelf types
        elif part_type_upper.startswith('OPEN SHELF'):
            return (L * P) * 2 + (H * P) * 2 + (L * H)
        
        # Shelf types (excluding SAFHE)
        elif part_type_upper.startswith('SHELF') and not part_type_upper.startswith('SAFHE'):
            factor_farsi = 2 * (2 * P + L + H)
            return (L * P) * 2 + (H * P) * 2 + (L * H) * 2 + factor_farsi
        
        # SAFHE types
        elif (part_type_upper.startswith('SAFHE 60') or part_type_upper.startswith('SAFHE 65') or
              part_type_upper.startswith('SAFHE 75') or part_type_upper.startswith('SAFHE 90') or
              part_type_upper.startswith('SAFHE 100') or part_type_upper.startswith('SAFHE 120')):
            return L
        
        # Ward types
        elif part_type_upper.startswith('WARD'):
            if P <= 0.30:
                factor_p = 0.45
            elif P <= 0.40:
                factor_p = 0.5
            elif P <= 0.50:
                factor_p = 0.55
            elif P <= 0.60:
                factor_p = 0.6
            elif P <= 0.70:
                factor_p = 0.65
            elif P <= 0.80:
                factor_p = 0.7
            elif P <= 0.90:
                factor_p = 0.75
            elif P <= 1.00:
                factor_p = 0.8
            elif P <= 1.10:
                factor_p = 0.85
            else:
                factor_p = 0.9
            
            return L * H * factor_p
        
        # Kesho types
        elif (part_type_upper.startswith('KESHO 1') or part_type_upper.startswith('KESHO 2') or
              part_type_upper.startswith('KESHO 3') or part_type_upper.startswith('KESHO 4')):
            return P * (H / 0.72) * L * 2
        
        # Tabaghe types
        elif part_type_upper.startswith('TABAGHE'):
            # Extract number from type
            if 'TABAGHE 1' in part_type_upper or part_type_upper == 'TABAGHE 1':
                multiplier = 1
            elif 'TABAGHE 2' in part_type_upper or part_type_upper == 'TABAGHE 2':
                multiplier = 2
            elif 'TABAGHE 3' in part_type_upper or part_type_upper == 'TABAGHE 3':
                multiplier = 3
            elif 'TABAGHE 4' in part_type_upper or part_type_upper == 'TABAGHE 4':
                multiplier = 4
            elif 'TABAGHE 5' in part_type_upper or part_type_upper == 'TABAGHE 5':
                multiplier = 5
            elif 'TABAGHE 6' in part_type_upper or part_type_upper == 'TABAGHE 6':
                multiplier = 6
            else:
                multiplier = 1
            
            return L * P * H * multiplier
        
        # Default case
        else:
            return 0
    
    def display_quantity_table(self):
        """Display the quantity table"""
        self.table_title.config(text="Quantity Table")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure columns
        columns = ['Type', 'L', 'P', 'H', 'Door Model', 'Color Category', 'Color Code', 'Formula Output']
        self.tree['columns'] = columns
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # Add data
        for _, row in self.quantity_df.iterrows():
            values = [
                row['Type'],
                f"{row['L']:.3f}",
                f"{row['P']:.3f}",
                f"{row['H']:.3f}",
                row['Door Model'],
                row['Color Category'],
                row['Color Code'],
                f"{row['Formula Output']:.4f}"
            ]
            self.tree.insert('', tk.END, values=values)
    
    def display_summary_table(self):
        """Display the summary table"""
        self.table_title.config(text="Summary Table")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure columns
        columns = ['Type Group', 'Door Model', 'Color Category', 'Color Code', 'Total Formula Output', 'Count']
        self.tree['columns'] = columns
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Add data
        for _, row in self.summary_df.iterrows():
            values = [
                row['Type_Group'],
                row['Door Model'],
                row['Color Category'],
                row['Color Code'],
                f"{row['Formula Output']:.4f}",
                row['Count']
            ]
            self.tree.insert('', tk.END, values=values)
    
    def display_cost_table(self):
        """Display the cost table (placeholder)"""
        self.table_title.config(text="Cost Table")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure columns for cost table (to be implemented)
        columns = ['Type', 'Color Category', 'Total Quantity', 'Unit Price', 'Total Cost']
        self.tree['columns'] = columns
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Placeholder message
        self.tree.insert('', tk.END, values=['Cost table implementation pending...', '', '', '', ''])
    
    def on_double_click(self, event):
        """Handle double-click for editing cells"""
        if self.current_view != "quantity":
            return  # Only allow editing in quantity table
        
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        column = self.tree.identify_column(event.x)
        column_index = int(column.replace('#', '')) - 1
        
        # Get current value
        values = list(self.tree.item(item, 'values'))
        current_value = values[column_index]
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Cell")
        edit_window.geometry("300x100")
        
        ttk.Label(edit_window, text="New value:").pack(pady=5)
        
        entry = ttk.Entry(edit_window, width=30)
        entry.pack(pady=5)
        entry.insert(0, current_value)
        entry.focus()
        
        def save_edit():
            new_value = entry.get()
            values[column_index] = new_value
            
            # Update the dataframe and recalculate if needed
            tree_index = self.tree.index(item)
            
            if column_index == 0:  # Type
                self.quantity_df.at[tree_index, 'Type'] = new_value
                # Recalculate formula for type change
                L = self.quantity_df.at[tree_index, 'L']
                P = self.quantity_df.at[tree_index, 'P']
                H = self.quantity_df.at[tree_index, 'H']
                
                new_formula_output = self.calculate_formula(new_value, L, P, H)
                self.quantity_df.at[tree_index, 'Formula Output'] = new_formula_output
                values[7] = f"{new_formula_output:.4f}"
                
            elif column_index in [1, 2, 3]:  # L, P, H
                try:
                    numeric_value = float(new_value)
                    col_name = ['L', 'P', 'H'][column_index - 1]
                    self.quantity_df.at[tree_index, col_name] = numeric_value
                    
                    # Recalculate formula
                    L = self.quantity_df.at[tree_index, 'L']
                    P = self.quantity_df.at[tree_index, 'P']
                    H = self.quantity_df.at[tree_index, 'H']
                    part_type = self.quantity_df.at[tree_index, 'Type']
                    
                    new_formula_output = self.calculate_formula(part_type, L, P, H)
                    self.quantity_df.at[tree_index, 'Formula Output'] = new_formula_output
                    values[7] = f"{new_formula_output:.4f}"
                except ValueError:
                    messagebox.showerror("Error", "Invalid numeric value")
                    return
            elif column_index == 4:  # Door Model
                self.quantity_df.at[tree_index, 'Door Model'] = new_value
            elif column_index == 5:  # Color Category
                self.quantity_df.at[tree_index, 'Color Category'] = new_value
            elif column_index == 6:  # Color Code
                self.quantity_df.at[tree_index, 'Color Code'] = new_value
            
            self.tree.item(item, values=values)
            edit_window.destroy()
        
        ttk.Button(edit_window, text="Save", command=save_edit).pack(pady=5)
        
        # Allow Enter key to save
        entry.bind('<Return>', lambda e: save_edit())
    
    def approve_and_next(self):
        """Handle approval and move to next table"""
        if self.current_view == "quantity":
            # Generate summary table
            # Add normalized type for grouping
            self.quantity_df['Type_Group'] = self.quantity_df['Type'].apply(self.normalize_type_for_summary)
            
            # Group by normalized type and other fields
            self.summary_df = self.quantity_df.groupby(
                ['Type_Group', 'Door Model', 'Color Category', 'Color Code']
            ).agg({
                'Formula Output': 'sum',
                'Type': 'count'  # Count of items
            }).reset_index()
            
            self.summary_df.rename(columns={'Type': 'Count'}, inplace=True)
            
            self.current_view = "summary"
            self.display_summary_table()
            self.back_button.config(state='normal')
            self.status_label.config(text=f"Summary table generated with {len(self.summary_df)} grouped entries")
            
        elif self.current_view == "summary":
            # Move to cost table
            self.current_view = "cost"
            self.display_cost_table()
            self.approve_button.config(state='disabled')
            self.status_label.config(text="Cost table (placeholder) displayed")
        
    def go_back(self):
        """Go back to previous table"""
        if self.current_view == "summary":
            self.current_view = "quantity"
            self.display_quantity_table()
            self.back_button.config(state='disabled')
            self.status_label.config(text="Returned to quantity table")
        elif self.current_view == "cost":
            self.current_view = "summary"
            self.display_summary_table()
            self.approve_button.config(state='normal')
            self.status_label.config(text="Returned to summary table")

if __name__ == "__main__":
    root = tk.Tk()
    app = PartsListProcessor(root)
    root.mainloop()
