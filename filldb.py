#Things to add/improve
#Rewrite entire thing so that the user does not have to break out to either the top of the function or back to main
#DB backup script
#potentially separate all the code chunks into their own files linked back to a main file
#bug fixing
#clean up the code/adjust spelling/grammar
#Pricing script partially rewritten for usability
#Find more areas to reduce required lines of code (condense commonly repeated things into a single function)
#Pricing script uses too many float() instead of simply making the variable a float to start with

import sqlite3

def usr_inp(prompt):
   inp = None
   inp = input(prompt)
   inp = inp.upper()
   if inp == '!Q':
       return "!Q"
   elif inp == '!R':
       return "!R"
   return inp if len(inp) > 0 else None

###################################
#START price script
###################################

def price():
    while True:
        conn = sqlite3.connect('filaments.db')
        c = conn.cursor()

        print("Enter '!Q' in any input box to return to top")
        print("Enter '!R' in any input box to reset current process\n")

        material = usr_inp("Enter your material: ")
        if material == '!Q':
            return
        if material == '!R':
            continue
        color = usr_inp("Enter material color: ")
        if color == '!Q':
            return
        if color == '!R':
            continue
        c.execute("SELECT * FROM filaments WHERE material=? AND color=?", (material,color))
        results = c.fetchall()
        if len(results) > 0 :
            for row in results:
                print(row)
        if len(results) < 1:
            print("No matching filaments")
            continue
        conn.commit()

        brand = usr_inp("Select filament brand: ")
        if brand == '!Q':
            return
        if brand == '!R':
            continue
        c.execute("SELECT * FROM filaments WHERE material=? AND color=? AND brand=?", (material,color,brand))
        results = c.fetchall()
        if len(results) < 1:
            print("Unknown filament brand")
            continue
        if len(results) > 0:
            for row in results:
                print(row)
            i_id = input("Select the ID of the filament you wish to select: ")
            if i_id.upper() == '!Q':
                return
            if i_id.upper() == '!R':
                continue
            c.execute("SELECT * FROM filaments WHERE id=?", (i_id))
            results = c.fetchall()
            conn.commit()
            if len(results) < 1:
                print("Unknown filament ID:", i_id)
                continue
            if len(results) > 0:
                print("Selected filament:", results)
        conn.commit()

        c.execute("SELECT price FROM filaments WHERE id=?", (i_id))
        p_result = c.fetchone()[0]
        if len(str(p_result)) > 0:
            print("Selected Price:", p_result)
        else:
            print("No price found")
        conn.commit()

        c.execute("SELECT size FROM filaments WHERE id=?", (i_id))
        sp_siz = c.fetchone()[0]
        conn.commit()

        p_gram = p_result / sp_siz

        wgt = usr_inp("Enter weight of print in grams: ")
        if wgt == '!Q':
            return
        if wgt == '!R':
            continue
        hrs = usr_inp("Enter print hours: ")
        if hrs == '!Q':
            return
        if hrs == '!R':
            continue
        mns = usr_inp("Enter print minutes: ")
        if mns == '!Q':
            return
        if mns == '!R':
            continue
        cst_hr = usr_inp("Enter cost/hr of printing: ")
        if cst_hr == '!Q':
            return
        if cst_hr == '!R':
            continue

        tim1 = float(hrs) * float(60)
        tim2 = float(tim1) + float(mns)
        tim3 = float(tim2) / float(60)

        wgt_cst = float(p_gram) * float(wgt)
        tim_cst = float(tim3) * float(cst_hr)
        cost = float(wgt_cst) + float(tim_cst)
        rnd_cost = round(cost, 2)
        print("$",rnd_cost)

        wgt_calc = input("Subtract estimated weight from selected filament? Y/N ")
        wgt_calc = wgt_calc.upper()
        if wgt_calc == '!R':
            continue
        if wgt_calc == '!Q':
            return
        if wgt_calc == 'Y':
            c.execute("SELECT weight FROM filaments WHERE id=?", (i_id))
            sp_wgt = c.fetchone()[0]
            conn.commit()
            c.execute("SELECT size FROM filaments WHERE id=?", (i_id))
            sp_size = c.fetchone()[0]
            conn.commit()
            c.execute("SELECT spools FROM filaments WHERE id=?", (i_id))
            sp_cnt = c.fetchone()[0]
            conn.commit()

            if float(sp_wgt) < float(wgt):
                print("ERROR: not enough material left on current spool")
                tot_wgt = ((float(sp_cnt) - 1) * sp_size) + float(sp_wgt)
                if float(tot_wgt) > float(wgt):
                    print("Total grams left:", tot_wgt)
                    print("Print can be completed with a filament change")
                    answer = input("Do you want to continue? Y/N: ")
                    answer = answer.upper()
                    if answer == 'N':
                        print("Process aborted")
                    if answer == '!Q':
                        return
                    if answer == '!R':
                        continue
                    if answer == 'Y':
                        n_tot_wgt = float(tot_wgt) - float(wgt)
                        n_sp_cnt = float(sp_cnt) - 1
                        c.execute('''UPDATE filaments SET weight=?
                                    WHERE id=?''', 
                                    (n_tot_wgt,i_id))
                        conn.commit()
                        c.execute('''UPDATE filaments SET spools=?
                                    WHERE id=?''', 
                                    (n_sp_cnt,i_id))
                        conn.commit()
                        c.execute("SELECT spools FROM filaments WHERE id=?",(i_id))
                        u_sp_cnt = c.fetchone()[0]
                        conn.commit()
                        c.execute("SELECT weght FROM filaments WHERE id=?", (i_id))
                        print("Process complete!")
                        print("Old spool count:", sp_cnt)
                        print("Old weight of current spool:", sp_wgt)
                        print("Updated spool count:", u_sp_cnt)
                        print("Updated weight of current spool:", u_sp_wgt)
                    else:
                        print("Invalid input")
                        continue

                if float(tot_wgt < float(wgt)):
                    print("Total grams left:", tot_wgt)
                    print("Not enough total material to complete print")
                    print("Select a new filament or update the number of spools")

            if float(sp_wgt) > float(wgt):
                n_wgt = float(sp_wgt) - float(wgt)
                c.execute("UPDATE filaments SET weight=? WHERE id=?", (n_wgt,i_id))
                conn.commit()
                c.execute("SELECT weight FROM filaments WHERE id=?", (i_id))
                u_sp_wgt = c.fetchone()[0]
                print("Old spool weight:", sp_wgt)
                print("Updated spool weight:", u_sp_wgt)
                conn.commit()                
        if wgt_calc == 'N':
            print("Operation Cancelled")
        else:
            print("Invalid input")
            continue

        conn.close()
        answer = input("Price another print? Y/N: ")
        answer = answer.upper()
        if answer == '!Q':
            return
        if answer == '!R':
            continue
        if answer == 'Y':
            continue
        if answer == 'N':
            return
        else:
            print("Invalid Input")
            return

###################################
#End pricing script
###################################

###################################
#START new entry script
###################################

def new():
    while True:
        conn = sqlite3.connect('filaments.db')
        c = conn.cursor()

        print("Enter '!Q' in any input box to return to top")
        print("Enter '!R' in any input box to reset current process")
        print("All fields are required\n")

        brand = usr_inp("Enter filament brand: ")
        if brand == '!Q':
            return
        if brand == '!R':
            continue
        material = usr_inp("Enter filament type: ")
        if material == '!Q':
            return
        if material == '!R':
            continue
        color = usr_inp("Enter filament color: ")
        if color == '!Q':
            return
        if color == '!R':
            continue
        spool = usr_inp("Enter the number of spools: ")
        if spool == '!Q':
            return
        if spool == '!R':
            continue
        size = usr_inp("Enter spool size in grams: ")
        if size == '!Q':
            return
        if size == '!R':
            continue
        weight = usr_inp("Enter spool weight in grams: ")
        if weight == '!Q':
            return
        if weight == '!R':
            continue
        price = usr_inp("Enter filament price per KG: ")
        if price == '!Q':
            return
        if price == '!R':
            continue

        print(brand,material,color,spool,size,weight,price)
        answer = input("Is this correct? Y/N: ")
        answer = answer.upper()
        if answer == '!Q':
            return
        if answer == '!R':
            continue
        if answer == 'N':
            continue
        if answer == 'Y':
            c.execute("SELECT * FROM filaments WHERE brand=? AND material=? AND color=? AND size=? AND price=?", (brand,material,color,size,price))
            results1 = c.fetchall()
            #print (results)
            conn.commit()
            if len(results1) > 0:
                print("Filament already exists. Duplicate entries will be ignored.")
                answer = input("Update spool count instead? Y/N: ")
                answer = answer.upper()
                if answer == 'N':                
                    print("Filament entry ignored. Reason: duplicate")
                    print("Process Complete!")
                if answer == 'Y':
                    c.execute("SELECT id FROM filaments WHERE brand=? AND material=? AND color=? AND size=? AND price=?", (brand,material,color,size,price))
                    r_id = c.fetchone()[0]
                    conn.commit()
                    r_id = str(r_id)
                    c.execute("SELECT spools FROM filaments WHERE id=?", (r_id))
                    results2 = c.fetchone()[0]
                    conn.commit()
                    n_sp_ct = float(results2) + float(spool)
                    n_sp_ct = str(n_sp_ct)
                    c.execute("UPDATE filaments SET spools=? WHERE id=?", (n_sp_ct,r_id))
                    conn.commit()
                    print("Process complete!")
                    print("New spool count:", n_sp_ct)
                if answer == '!Q':
                    return
                if answer == '!R':
                    continue
                else:
                    print("Invalid input")
                    continue
            if len(results1) < 1:
                    c.execute('''
                            INSERT OR IGNORE INTO filaments (brand, material, color, spools, size, weight, price)

                            VALUES
                            (?, ?, ?, ?, ?, ?, ?)

                            ''', (brand,material,color,spool,size,weight,price))
                    conn.commit()
                    print("Process complete!")
        else:
            print("Invalid input")
            continue

        conn.close()
        answer = input("Add another filament? Y/N: ")
        answer = answer.upper()
        if answer == 'Y':
            continue
        if answer == 'N':
            return
        if answer == '!Q':
            return
        if answer == '!R':
            continue
        else:
            print("Invalid Input")
            return

###################################
#End filament entry script
###################################

###################################
#START Search for a filament
###################################

def search():
    while True:
        conn = sqlite3.connect('filaments.db')
        c = conn.cursor()

        print("Enter '!Q' in any input box to return to top")
        print("Enter '!R' in any input box to reset current process")
        print("Enter a value or leave blank\n")

        brand = usr_inp("Enter brand: ")
        if brand == '!Q':
            return
        if brand == '!R':
            continue
        material = usr_inp("Enter material: ")
        if material == '!Q':
            return
        if material == '!R':
            continue
        color = usr_inp("Enter color: ")
        if color == '!Q':
            return
        if color == '!R':
            continue
        spool = usr_inp("Enter spool count: ")
        if spool == '!Q':
            return
        if spool == '!R':
            continue
        size = usr_inp("Enter spool size: ")
        if size == '!Q':
            return
        if size == '!R':
            continue
        price = usr_inp("Enter price: ")
        if price == '!Q':
            return
        if price == '!R':
            continue
        #print(brand, material, color, price)

        c.execute('''SELECT * FROM filaments 
                  WHERE brand= COALESCE(?, brand) 
                  AND material= COALESCE(?, material)
                  AND color= COALESCE(?, color)
                  AND spools= COALESCE(?, spools)
                  AND size= COALESCE(?, size)
                  AND price= COALESCE(?, price)''', (brand,material,color,spool,size,price,))
        results = c.fetchall()
        conn.commit()
        if len(results) > 0:
            print("Matching Filaments:\n")
            for row in results:
                print(row)

        conn.close()
        answer = input("Search again? Y/N: ")
        answer = answer.upper()
        if answer == '!Q':
            return
        if answer == '!R':
            continue
        if answer == 'Y':
            continue
        if answer == 'N':
            return
        else:
            print("Invalid Input")
            return


###################################
#End filament search script
###################################

###################################
#START database update script
###################################

def update():
    while True:
        conn = sqlite3.connect('filaments.db')
        c = conn.cursor()

        print("Enter '!Q' in any input box to return to top")
        print("Enter '!R' in any input box to reset current process")
        print("Enter a value or leave bank\n")

        brand = usr_inp("What brand filament do you want to update/change? ")
        if brand == '!Q':
            return
        if brand == '!R':
            continue
        material = usr_inp("What material type? ")
        if material == '!Q':
            return
        if material == '!R':
            continue  
        color = usr_inp("what color? ")
        if color == '!Q':
            return
        if color == '!R':
            continue
        size = usr_inp("What spool size? ")
        if size == '!Q':
            return
        if size == '!R':
            continue
        price = usr_inp("What price? ")
        if price == '!Q':
            return
        if price == '!R':
            continue

        c.execute('''SELECT * FROM filaments WHERE brand= COALESCE(?,brand) 
                  AND material= COALESCE(?,material)
                  AND color= COALESCE(?, color)
                  AND size= COALESCE(?, size)
                  AND price= COALESCE(?, price)''', (brand,material,color,size,price))
        results = c.fetchall()
        conn.commit()
        for row in results:
            print(row)

        slct = input("Enter the ID of the filament you would like to update: ")
        if slct.upper() == '!Q':
            return
        if slct.upper() == '!R':
            continue

        c.execute("SELECT * FROM filaments WHERE id=?", (slct))
        results = c.fetchall()
        print(results)
        if len(results) > 0:
            print("Which value do you want to update?")
            print("brand, material, color, spools, size, weight, price, all")
            updt = input("Selection: ")
            updt = updt.lower()
            if updt.upper() == '!Q':
                return
            if updt.upper() == '!R':
                continue

            inp_lst = ["brand", "material", "color", "spools", "size", "weight", "price"]
            if updt in inp_lst:
                nval = input("Enter new value: ")
                nval = nval.upper()
                c.execute(f"UPDATE filaments SET {updt}=? WHERE id=?", (nval,slct))
                conn.commit()
                print(f"Process complete!\nNew Value: {updt} = {nval}")

            if updt == 'all':

                print("Enter new value or leave blank")
                b = usr_inp("Enter new brand: ")
                if b == '!Q':
                    return
                if b == '!R':
                    continue
                m = usr_inp("Enter new material: ")
                if m == '!Q':
                    return
                if m == '!R':
                    continue
                co = usr_inp("Enter new color: ")
                if co == '!Q':
                    return
                if co == '!R':
                    continue
                sc = usr_inp("Enter new spool count ")
                if sc == '!Q':
                    return
                if sc == '!R':
                    continue
                ss = usr_inp("Enter new spool size: ")
                if ss == '!Q':
                    return
                if ss == '!R':
                    continue
                sw = usr_inp("Enter new spool weight: ")
                if sw == '!Q':
                    return
                if sw == '!R':
                    continue
                p = usr_inp("Enter new price: ")
                if p == '!Q':
                    return
                if p == '!R':
                    continue

                print(b,m,co,sc,ss,sw,p,slct)
                answer = input("Is this correct? Y/N: ")
                answer = answer.upper()
                if answer == 'Y':
                    c.execute('''UPDATE filaments SET 
                            brand= COALESCE(?,brand),
                            material= COALESCE(?,material),
                            color= COALESCE(?, color),
                            spools= COALESCE(?, spools),
                            size= COALESCE(?, size),
                            weight= COALESCE(?, weight),
                            price= COALESCE(?, price)
                            WHERE id=?''', (b,m,co,sc,ss,sw,p,slct))
                    conn.commit()
                    print("Process complete!")
                    c.execute("SELECT * FROM filaments WHERE id=?",(slct))
                    results = c.fetchall()
                    conn.commit()
                    print("New Values:\n",results)
                if answer == 'N':
                    continue
                if answer == '!Q':
                    return
                if answer == '!R':
                    continue
                else:
                    print("Invalid input")
                    continue
            
            if updt not in inp_lst:
                print("Invalid input")
                continue
        
        if len(results) < 1:
            print("Invalid ID")
            continue

        conn.close()
        answer = input("Update another filament? Y/N: ")
        answer = answer.upper()
        if answer == 'Y':
            continue
        if answer == 'N':
            return
        if answer == '!Q':
            return
        if answer == '!R':
            continue
        else:
            print("Invalid Input")
            return

###################################
#END update script
###################################

###################################
#START database delete script
###################################

def delete():
    while True:
        conn = sqlite3.connect('filaments.db')
        c = conn.cursor()
    
        print("Enter '!Q' in any input box to return to top")
        print("Enter '!R' in any input box to reset current process")
        print("Fill out each box or leave blank if unsure\n")


        brand = usr_inp("What brand of filament do you want to delete? ")
        if brand == '!Q':
            return
        if brand == '!R':
            continue
        material = usr_inp("What material type? ")
        if material == '!Q':
            return
        if material == '!R':
            continue    
        color = usr_inp("what color? ")
        if color == '!Q':
            return
        if color == '!R':
            continue
        size = usr_inp("What spool size? ")
        if size == '!Q':
            return
        if size == '!R':
            continue
        price = usr_inp("What price? ")
        if price == '!Q':
            return
        if price == '!R':
            continue

        c.execute('''SELECT * FROM filaments 
                  WHERE brand= COALESCE(?, brand) 
                  AND material= COALESCE(?, material)
                  AND color= COALESCE(?, color)
                  AND size= COALESCE(?, size)
                  AND price= COALESCE(?, price)''', (brand,material,color,size,price))
        results = c.fetchall()
        conn.commit()
        for row in results:
            print(row)

        slct = input("Enter the ID of the filament you want to delete: ")
        if slct.upper() == '!Q':
            return
        if slct.upper() == '!R':
            continue

        c.execute("SELECT * FROM filaments WHERE id=?", (slct))
        results = c.fetchall()
        conn.commit()
        if len(results) > 0:
            print("Selected filament:\n", results)
        if len(results) < 1:
            print("Invalid ID")

        answer = input("Do you want to delete this filament entry? Y/N: ")
        answer= answer.upper()
        if answer == 'N':
            print("Operation cancelled")
        if answer == '!Q':
            return
        if answer == '!R':
            continue
        if answer == 'Y':
            c.execute("DELETE FROM filaments WHERE id=?", (slct))
            conn.commit()
            print("Process complete!")
        else:
            print("Invalid input")
            continue

        conn.close()
        answer = input("Delete another entry? Y/N: ")
        answer = answer.upper()
        if answer == 'Y':
            continue
        if answer == 'N':
            return
        if answer == '!Q':
            return
        if answer == '!R':
            continue
        else:
            print("Invalid Input")
            return

conn = sqlite3.connect('filaments.db')
c = conn.cursor()
###################################
#END database delete script
###################################

###################################
#START opening code
###################################

c.execute('''
          CREATE TABLE IF NOT EXISTS filaments
          ([id] INTEGER PRIMARY KEY AUTOINCREMENT,
          [brand] TEXT,
          [material] TEXT,
          [color] TEXT,
          [spools] INTEGER,
          [size] INTEGER,
          [weight] INTEGER,
          [price] INTEGER
          )
          ''')
conn.commit()
conn.close()

print("Created by Caleb Kreifels\n")
print("Welcome! What would you like to do?\nFor a list of commands type 'LIST'.\nType 'QUIT' to save and exit.\nType INFO for information and instructions.")

while True:
    conn = sqlite3.connect('filaments.db')
    c = conn.cursor()
    comlst = ("QUIT", "LIST", "PRICE", "NEW", "SEARCH", "UPDATE", "DELETE", "INFO", "SAVE")
    op1 = input("Enter a command: ")
    op1 = op1.upper()
    if op1 == 'QUIT' :
        print("Goodbye!")
        conn.close()
        quit()

    if op1 == 'LIST' :
        print(comlst)

    if op1 == 'PRICE':
        price()

    if op1 == 'NEW':
        new()

    if op1 == 'SEARCH':
        search()
    
    if op1 == 'UPDATE':
        update()
    
    if op1 == 'DELETE':
        delete()

    if op1 == 'SAVE':
        conn.close()
        conn = sqlite3.connect('filaments.db')
        c = conn.cursor()

    if op1 == 'INFO':
        print("\n\nFilDB V0.75\n\n")
        print("This is a database for your personal 3D printer filaments.")
        print("Features include:\nPricing calculator\nAutomatic spool count tracker\nAutomatic filament usage calculator that tracks how much filament is left on the given spool.\n")
        print("------------------------------\n")
        print("Do NOT cloe the program in any way aside from using the 'QUIT' command in the main promt. I can not guaruntee your changes will be saved otherwise.\n")
        print("------------------------------\n")
        print("IMPORTANT: spool weight is the current weight of the material left on the spool. Spool size is the rated size of the spool (250g, 1000, 2000g, etc.).\nWhen entering a new spool, the spool size and spool weight need to be the same other wise the calculators will not work.\n")
        print("------------------------------\n")
        print("IMPORTANT: The ID is the first column of printed results. This value is automatic and unchanging. You will need this ID number when performing many functions.\n")
        print("------------------------------\n")
        print("IMPORTANT: The database follows this order: id, brand, material, color, spools, size, weight, price.\nThis will be very useful when using this program.\n")
        print("Thank you for using my tool!\nPlease send feedback and bugs to:\n\ninsulatedmango@gmail.com\n\nand for professional inquiries only message here:\n\nhttps://www.linkedin.com/in/caleb-k-0b92a525a/")

    else:
        continue

###################################
#END opening code
###################################
