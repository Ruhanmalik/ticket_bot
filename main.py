import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

def send_comp_tickets_from_csv(csv_file_path, ticket_type="General", delay=3, pause_every=10):
    """
    Automate sending comp tickets from a CSV file.
    CSV columns: "first name", "last name", "email", "quantity"
    """
    
    # Read CSV file
    with open(csv_file_path, 'r') as file:
        csv_reader = list(csv.DictReader(file))
        
    if not csv_reader:
        print("❌ CSV file is empty!")
        return
    
    print(f"\n📋 CSV columns found: {list(csv_reader[0].keys())}")
    print(f"📊 Total people: {len(csv_reader)}")
    print(f"⏸️  Will pause every {pause_every} submissions\n")
    
    response = input("Ready to start? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Cancelled")
        return
    
    total_processed = 0
    successful = 0
    failed = 0
    total_tickets = 0
    
    try:
        for index, row in enumerate(csv_reader, 1):
            # Handle column names with spaces
            first_name = row['first name'].strip()
            last_name = row['last name'].strip()
            email = row['email'].strip()
            quantity = row['quantity'].strip()
            
            print(f"\n[{index}/{len(csv_reader)}] {first_name} {last_name} ({email}) - Qty: {quantity}")
            
            try:
                wait = WebDriverWait(driver, 10)
                
                # Fill in First Name
                first_name_field = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Jane']"))
                )
                first_name_field.clear()
                first_name_field.send_keys(first_name)
                
                # Fill in Last Name
                last_name_field = driver.find_element(By.XPATH, "//input[@placeholder='Doe']")
                last_name_field.clear()
                last_name_field.send_keys(last_name)
                
                # Fill in Email
                email_field = driver.find_element(By.XPATH, "//input[@placeholder='jane@example.com']")
                email_field.clear()
                email_field.send_keys(email)
                
                # Select Ticket Type from dropdown
                ticket_type_select = Select(driver.find_element(By.XPATH, "//select"))
                ticket_type_select.select_by_visible_text(ticket_type)
                
                # Set Quantity
                quantity_field = driver.find_element(By.XPATH, "//input[@type='number']")
                quantity_field.clear()
                quantity_field.send_keys(quantity)
                
                # Clear Comp Reason
                comp_reason_field = driver.find_element(By.XPATH, "//input[@placeholder='Volunteer staff']")
                comp_reason_field.clear()
                
                # Check checkbox
                email_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
                if not email_checkbox.is_selected():
                    email_checkbox.click()
                
                # Click Send button
                send_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Comp Tickets')]")
                send_button.click()
                
                time.sleep(delay)
                
                print(f"    ✓ Sent {quantity} ticket(s)")
                successful += 1
                total_tickets += int(quantity)
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                failed += 1
                cont = input("    Continue? (yes/skip/stop): ").strip().lower()
                if cont == 'stop':
                    break
                elif cont == 'skip':
                    continue
            
            total_processed += 1
            
            # Pause checkpoint
            if total_processed % pause_every == 0 and total_processed < len(csv_reader):
                print(f"\n⏸️  Paused after {total_processed}")
                print(f"   ✓ {successful} | ✗ {failed} | 🎟️ {total_tickets} tickets")
                if input("   Continue? (yes/no): ").strip().lower() != 'yes':
                    break
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by Ctrl+C")
    
    finally:
        # Summary
        print("\n" + "="*60)
        print(f"SUMMARY:")
        print(f"People: {total_processed}/{len(csv_reader)}")
        print(f"Success: {successful} | Failed: {failed}")
        print(f"Total tickets sent: {total_tickets}")
        print("="*60)

if __name__ == "__main__":
    # Setup Chrome with persistent session (stays logged in)
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=./chrome_session")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://ticketbud.com/admin/events/fe2e84b6-f627-11f0-bed6-42010a7170e9/orders/comps/new")
        
        input("Press Enter after logging in (only needed first time)...")
        
        csv_file = "test.csv"
        ticket_type = "General"
        
        send_comp_tickets_from_csv(
            csv_file_path=csv_file,
            ticket_type=ticket_type,
            delay=3,
            pause_every=10
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Cancelled")
    finally:
        print("\nClosing browser in 5 seconds...")
        time.sleep(5)
        driver.quit()