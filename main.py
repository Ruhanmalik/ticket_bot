import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

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
                wait = WebDriverWait(driver, 15)
                
                # Fill in First Name
                first_name_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Jane']"))
                )
                first_name_field.clear()
                first_name_field.send_keys(first_name)
                time.sleep(0.2)
                
                # Fill in Last Name
                last_name_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Doe']"))
                )
                last_name_field.clear()
                last_name_field.send_keys(last_name)
                time.sleep(0.2)
                
                # Fill in Email
                email_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='jane@example.com']"))
                )
                email_field.clear()
                email_field.send_keys(email)
                time.sleep(0.2)
                
                # Select Ticket Type
                dropdown_element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//select"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_element)
                time.sleep(0.3)
                dropdown_element.click()
                time.sleep(0.3)
                
                ticket_type_select = Select(dropdown_element)
                ticket_type_select.select_by_visible_text(ticket_type)
                time.sleep(0.2)
                
                # Set Quantity
                quantity_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='number']"))
                )
                quantity_field.clear()
                time.sleep(0.1)
                quantity_field.send_keys(quantity)
                time.sleep(0.2)
                
                # Clear Comp Reason
                comp_reason_field = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Volunteer staff']"))
                )
                comp_reason_field.clear()
                time.sleep(0.2)
                
                # Check checkbox
                email_checkbox = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
                )
                if not email_checkbox.is_selected():
                    email_checkbox.click()
                time.sleep(0.2)
                
                # Click Send Comp Tickets button
                print("    📤 Clicking 'Send Comp Tickets' button...")
                send_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Comp Tickets')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
                time.sleep(0.3)
                
                # Use JavaScript click as backup if regular click doesn't work
                try:
                    send_button.click()
                except:
                    driver.execute_script("arguments[0].click();", send_button)
                
                print("    ⏳ Waiting for redirect to Orders page...")
                time.sleep(delay)
                
                # Wait for redirect to Orders page and click "+ Comp Tickets" to go back
                try:
                    print("    🔄 Looking for '+ Comp Tickets' button...")
                    comp_tickets_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Comp Tickets')] | //*[contains(text(), '+ Comp Tickets')]"))
                    )
                    print("    ✓ Found button, clicking to return to form...")
                    comp_tickets_button.click()
                    time.sleep(1)  # Wait for form to load
                    print("    ✓ Back at form")
                except Exception as e:
                    print(f"    ⚠️  Could not find '+ Comp Tickets' button: {e}")
                    # Try navigating directly back to the form
                    print("    🔄 Navigating directly back to form...")
                    driver.get("https://ticketbud.com/admin/events/fe2e84b6-f627-11f0-bed6-42010a7170e9/orders/comps/new")
                    time.sleep(2)
                
                print(f"    ✓ Sent {quantity} ticket(s)")
                successful += 1
                total_tickets += int(quantity)
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                print(f"    Error type: {type(e).__name__}")
                failed += 1
                
                # Try to recover by going back to the form
                try:
                    print("    🔄 Attempting to recover...")
                    driver.get("https://ticketbud.com/admin/events/fe2e84b6-f627-11f0-bed6-42010a7170e9/orders/comps/new")
                    time.sleep(2)
                except:
                    pass
                
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