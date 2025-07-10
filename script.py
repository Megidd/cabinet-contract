import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import re

class PartsListProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Parts List Processor")
        self.root.geometry("1200x800")
        
        # Data storage
        self.parts_data = None
        self.price_table = []
        self.intermediate_df = None
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # File upload section
        upload_frame = ttk.LabelFrame(main_frame, text="Upload Parts List", padding="5")
        upload_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.file_label = ttk.Label(upload_frame, text="No file selected")
        self.file_label.grid(row=0, column=0, padx=5)
        
        ttk.Button(upload_frame, text="Browse", command=self.browse_file).grid(row=0, column=1, padx=5)
        ttk.Button(upload_frame, text="Process File", command=self.process_file).grid(row=0, column=2, padx=5)
        
        # Price table section
        price_frame = ttk.LabelFrame(main_frame, text="Price Table", padding="5")
        price_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Price table headers
        ttk.Label(price_frame, text="Type").grid(row=0, column=0, padx=5)
        ttk.Label(price_frame, text="Color").grid(row=0, column=1, padx=5)
        ttk.Label(price_frame, text="Price").grid(row=0, column=2, padx=5)
        
        # Price table entry fields
        self.type_entry = ttk.Entry(price_frame, width=20)
        self.type_entry.grid(row=1, column=0, padx=5)
        
        self.color_entry = ttk.Entry(price_frame, width=20)
        self.color_entry.grid(row=1, column=1, padx=5)
        
        self.price_entry = ttk.Entry(price_frame, width=20)
        self.price_entry.grid(row=1, column=2, padx=5)
        
        ttk.Button(price_frame, text="Add Price Entry", command=self.add_price_entry).grid(row=1, column=3, padx=5)
        
        # Price table display
        self.price_listbox = tk.Listbox(price_frame, height=5, width=60)
        self.price_listbox.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        
        # Intermediate table section
        intermediate_frame = ttk.LabelFrame(main_frame, text="Intermediate Table", padding="5")
        intermediate_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        intermediate_frame.columnconfigure(0, weight=1)
        intermediate_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for intermediate table
        self.tree = ttk.Treeview(intermediate_frame, columns=('Type', 'L', 'P', 'H', 'Door Model', 'Color', 'Color Code', 'Formula Output'), show='headings')
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Define column headings
        self.tree.heading('Type', text='Type')
        self.tree.heading('L', text='L')
        self.tree.heading('P', text='P')
        self.tree.heading('H', text='H')
        self.tree.heading('Door Model', text='Door Model')
        self.tree.heading('Color', text='Color')
        self.tree.heading('Color Code', text='Color Code')
        self.tree.heading('Formula Output', text='Formula Output')
        
        # Configure column widths
        for col in self.tree['columns']:
            self.tree.column(col, width=140)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(intermediate_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(intermediate_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Edit functionality
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Final table button
        ttk.Button(main_frame, text="Generate Final Table", command=self.generate_final_table).grid(row=4, column=0, pady=10)
        
        # Final table section (placeholder)
        final_frame = ttk.LabelFrame(main_frame, text="Final Table", padding="5")
        final_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.final_label = ttk.Label(final_frame, text="Final table will be displayed here after processing")
        self.final_label.grid(row=0, column=0)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Parts List File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_label.config(text=filename.split('/')[-1])
            self.filename = filename
    
    def add_price_entry(self):
        type_val = self.type_entry.get()
        color_val = self.color_entry.get()
        price_val = self.price_entry.get()
        
        if type_val and color_val and price_val:
            try:
                price_float = float(price_val)
                self.price_table.append((type_val, color_val, price_float))
                self.price_listbox.insert(tk.END, f"{type_val} | {color_val} | ${price_float}")
                
                # Clear entries
                self.type_entry.delete(0, tk.END)
                self.color_entry.delete(0, tk.END)
                self.price_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Price must be a number")
    
    def process_file(self):
        if not hasattr(self, 'filename'):
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            # Read the file with tab separator
            with open(self.filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Process lines
            intermediate_data = []
            
            for line in lines:
                columns = line.strip().split('\t')
                
                # Check if first column contains 'ADIN'
                if len(columns) >= 14 and 'ADIN' in columns[0]:
                    try:
                        # Extract required columns
                        part_type = columns[1] if len(columns) > 1 else ""
                        L = float(columns[3]) if len(columns) > 3 and columns[3] else 0
                        P = float(columns[4]) if len(columns) > 4 and columns[4] else 0
                        H = float(columns[5]) if len(columns) > 5 and columns[5] else 0
                        door_model = columns[10] if len(columns) > 10 else ""
                        color = columns[12] if len(columns) > 12 else ""
                        color_code = columns[13] if len(columns) > 13 else ""
                        
                        # Calculate formula output
                        formula_output = self.calculate_formula(part_type, L, P, H)
                        
                        # Add to tree
                        self.tree.insert('', tk.END, values=(part_type, L, P, H, door_model, color, color_code, f"{formula_output:.2f}"))
                        
                        intermediate_data.append({
                            'Type': part_type,
                            'L': L,
                            'P': P,
                            'H': H,
                            'Door Model': door_model,
                            'Color': color,
                            'Color Code': color_code,
                            'Formula Output': formula_output
                        })
                    except (ValueError, IndexError) as e:
                        continue
            
            self.intermediate_df = pd.DataFrame(intermediate_data)
            messagebox.showinfo("Success", f"Processed {len(intermediate_data)} ADIN entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {str(e)}")
    
    def calculate_formula(self, part_type, L, P, H):
        """Calculate formula based on part type"""
        part_type_upper = part_type.upper()
        
        # Base and Tall types
        if part_type_upper.startswith('BASE') or part_type_upper.startswith('TALL'):
            return (P/100) * (H/72) * L/100
        
        # Wall types
        elif part_type_upper.startswith('WALL'):
            # Calculate Factor_H
            if H <= 40:
                factor_h = 0.25
            elif H <= 50:
                factor_h = 0.30
            elif H <= 60:
                factor_h = 0.35
            elif H <= 70:
                factor_h = 0.40
            else:
                factor_h = 0.40 + (H - 70) / 100
            
            # Calculate Factor_P
            factor_p = (P - 30) / 200
            
            return (factor_h + factor_p) * L
        
        # NAMA U types
        elif part_type_upper.startswith('NAMA U'):
            return (P + L + 8) * H
        
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
            return L * P + (L / 100) * factor_light
        
        # NAMA ver with light types
        elif part_type_upper.startswith('NAMA VER WITH LIGHT'):
            factor_light = 550
            return H * P + (H / 100) * factor_light
        
        # Open shelf types
        elif part_type_upper.startswith('OPEN SHELF'):
            return (L * P) * 2 + (H * P) * 2 + (L * H)
        
        # Shelf types
        elif part_type_upper.startswith('SHELF'):
            factor_farsi = 2 * (2 * P + L + H)
            return (L * P) * 2 + (H * P) * 2 + (L * H) * 2 + factor_farsi
        
        # SAFHE 60 types
        elif part_type_upper.startswith('SAFHE 60'):
            # Look up price from price table
            factor_price = self.lookup_price(part_type, '')  # Color would be needed here
            return (L / 100) * factor_price
        
        # SAFHE 65-120, Ward, Kesho, Tabaghe types
        elif (part_type_upper.startswith('SAFHE 65') or part_type_upper.startswith('SAFHE 75') or
              part_type_upper.startswith('SAFHE 90') or part_type_upper.startswith('SAFHE 100') or
              part_type_upper.startswith('SAFHE 120') or part_type_upper.startswith('KESHO') or
              part_type_upper.startswith('TABAGHE')):
            return L + P + H
        
        # Ward types
        elif part_type_upper.startswith('WARD'):
            if P <= 30:
                factor_p = 0.45
            elif P <= 40:
                factor_p = 0.5
            elif P <= 50:
                factor_p = 0.55
            elif P <= 60:
                factor_p = 0.6
            elif P <= 70:
                factor_p = 0.65
            elif P <= 80:
                factor_p = 0.7
            elif P <= 90:
                factor_p = 0.75
            elif P <= 100:
                factor_p = 0.8
            elif P <= 110:
                factor_p = 0.85
            else:
                factor_p = 0.9
            
            return L * H * factor_p
        
        # Default case
        else:
            return 0
    
    def lookup_price(self, type_val, color_val):
        """Look up price from price table"""
        for entry in self.price_table:
            if entry[0] == type_val and entry[1] == color_val:
                return entry[2]
        return 1  # Default price if not found
    
    def on_double_click(self, event):
        """Handle double-click for editing cells"""
        item = self.tree.selection()[0]
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
            
            # Recalculate formula if numeric columns changed
            if column_index in [1, 2, 3]:  # L, P, H columns
                try:
                    L = float(values[1])
                    P = float(values[2])
                    H = float(values[3])
                    values[7] = f"{self.calculate_formula(values[0], L, P, H):.2f}"
                except ValueError:
                    pass
            
            self.tree.item(item, values=values)
            edit_window.destroy()
        
        ttk.Button(edit_window, text="Save", command=save_edit).pack(pady=5)
        
        # Allow Enter key to save
        entry.bind('<Return>', lambda e: save_edit())
    
    def generate_final_table(self):
        """Generate final table (placeholder)"""
        messagebox.showinfo("Info", "Final table generation will be implemented later")

if __name__ == "__main__":
    root = tk.Tk()
    app = PartsListProcessor(root)
    root.mainloop()
