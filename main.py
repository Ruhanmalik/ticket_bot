import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

def highlight_element(driver, element, color="yellow", border=3, duration=0.5):
    """Visually highlight an element before clicking it"""
    original_style = element.get_attribute('style')
    highlight_style = f"background: {color} !important; border: {border}px solid red !important; transition: all 0.2s;"
    driver.execute_script(f"arguments[0].setAttribute('style', '{highlight_style}');", element)
    time.sleep(duration)
    driver.execute_script(f"arguments[0].setAttribute('style', '{original_style or ''}');", element)

def click_with_visual(driver, element, name="element"):
    """Click an element with visual feedback"""
    print(f"    🎯 Highlighting '{name}'...")
    highlight_element(driver, element, color="#ffff00", duration=0.3)
    
    # Scroll element into view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.2)
    
    # Try multiple click methods
    try:
        # Method 1: Regular click
        print(f"    🖱️  Attempting regular click on '{name}'...")
        element.click()
        print(f"    ✅ Regular click succeeded!")
        return True
    except Exception as e:
        print(f"    ⚠️  Regular click failed: {e}")
    
    try:
        # Method 2: JavaScript click
        print(f"    🖱️  Attempting JS click on '{name}'...")
        driver.execute_script("arguments[0].click();", element)
        print(f"    ✅ JS click succeeded!")
        return True
    except Exception as e:
        print(f"    ⚠️  JS click failed: {e}")
    
    try:
        # Method 3: ActionChains click
        print(f"    🖱️  Attempting ActionChains click on '{name}'...")
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).move_to_element(element).click().perform()
        print(f"    ✅ ActionChains click succeeded!")
        return True
    except Exception as e:
        print(f"    ⚠️  ActionChains click failed: {e}")
    
    return False

def send_comp_tickets_from_csv(driver, csv_file_path, ticket_type="General", delay=3, pause_every=10):
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
    
    base_url = driver.current_url
    
    try:
        for index, row in enumerate(csv_reader, 1):
            first_name = row['first name'].strip()
            last_name = row['last name'].strip()
            email = row['email'].strip()
            quantity = row['quantity'].strip()
            
            print(f"\n{'='*60}")
            print(f"[{index}/{len(csv_reader)}] {first_name} {last_name} ({email}) - Qty: {quantity}")
            print('='*60)
            
            try:
                wait = WebDriverWait(driver, 15)
                
                # Fill in First Name
                print("    📝 Filling First Name...")
                first_name_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Jane']"))
                )
                highlight_element(driver, first_name_field, color="#90EE90", duration=0.2)
                first_name_field.clear()
                first_name_field.send_keys(first_name)
                time.sleep(0.2)
                
                # Fill in Last Name
                print("    📝 Filling Last Name...")
                last_name_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Doe']"))
                )
                highlight_element(driver, last_name_field, color="#90EE90", duration=0.2)
                last_name_field.clear()
                last_name_field.send_keys(last_name)
                time.sleep(0.2)
                
                # Fill in Email
                print("    📝 Filling Email...")
                email_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='jane@example.com']"))
                )
                highlight_element(driver, email_field, color="#90EE90", duration=0.2)
                email_field.clear()
                email_field.send_keys(email)
                time.sleep(0.2)
                
                # Select Ticket Type
                print("    📝 Selecting Ticket Type...")
                dropdown_element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//select"))
                )
                highlight_element(driver, dropdown_element, color="#90EE90", duration=0.2)
                driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_element)
                time.sleep(0.3)
                ticket_type_select = Select(dropdown_element)
                ticket_type_select.select_by_visible_text(ticket_type)
                time.sleep(0.3)  # Wait a bit longer for any JS to process
                
                # Set Quantity from CSV
                print(f"    📝 Setting Quantity to {quantity}...")
                quantity_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='number']"))
                )
                highlight_element(driver, quantity_field, color="#90EE90", duration=0.2)
                quantity_field.clear()
                time.sleep(0.1)
                quantity_field.send_keys(quantity)
                time.sleep(0.2)
                
                # Skip comp reason and checkbox - they're already set correctly by default
                print("    ✓ Comp reason and checkbox are already set correctly, skipping...")
                
                time.sleep(0.2)
                
                # ===== Click the "Send Comp Tickets" button =====
                print("    🔴 Looking for 'Send Comp Tickets' button...")
                
                # CRITICAL: Verify quantity matches CSV value right before clicking
                print(f"    🔍 Final check: Verifying quantity is {quantity} before submitting...")
                try:
                    quantity_field_final = driver.find_element(By.XPATH, "//input[@type='number']")
                    qty_final = quantity_field_final.get_attribute("value")
                    print(f"    📊 Final quantity value: {qty_final}")
                    if qty_final != quantity and qty_final != f"{quantity}.0":
                        print(f"    ⚠️  Quantity is {qty_final}, expected {quantity}. Setting to {quantity}...")
                        quantity_field_final.clear()
                        time.sleep(0.1)
                        quantity_field_final.send_keys(quantity)
                        time.sleep(0.2)
                        print(f"    ✓ Quantity set to {quantity}")
                    elif qty_final == "":
                        print(f"    ⚠️  Quantity field is empty, setting to {quantity}...")
                        quantity_field_final.send_keys(quantity)
                        time.sleep(0.2)
                    else:
                        print(f"    ✓ Quantity is {quantity}, good to go!")
                except Exception as qty_error:
                    print(f"    ⚠️  Could not verify/set quantity: {qty_error}")
                    print("    📌 Proceeding anyway...")
                
                # Wait a moment for any dynamic content
                time.sleep(0.3)
                
                submit_button = None
                
                # The button might be a <button>, <a>, <input>, or <div> - search all
                selectors_to_try = [
                    # XPath selectors for any element with this text
                    ("xpath", "//*[normalize-space()='Send Comp Tickets']"),
                    ("xpath", "//*[contains(text(), 'Send Comp Tickets')]"),
                    ("xpath", "//a[contains(text(), 'Send Comp Tickets')]"),
                    ("xpath", "//button[contains(text(), 'Send Comp Tickets')]"),
                    ("xpath", "//input[@value='Send Comp Tickets']"),
                    # CSS selectors for common button classes
                    ("css", "a.btn-danger"),
                    ("css", "a[class*='danger']"),
                    ("css", ".btn-danger"),
                    ("css", "[class*='btn'][class*='danger']"),
                    ("css", "input[type='submit']"),
                ]
                
                for sel_type, selector in selectors_to_try:
                    try:
                        if sel_type == "xpath":
                            submit_button = driver.find_element(By.XPATH, selector)
                        else:
                            submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if submit_button and submit_button.is_displayed():
                            print(f"    ✓ Found submit element with {sel_type}: {selector}")
                            print(f"    ✓ Element tag: <{submit_button.tag_name}>, text: '{submit_button.text.strip()}'")
                            break
                    except:
                        submit_button = None
                        continue
                
                # If still not found, search ALL clickable elements
                if not submit_button:
                    print("    🔍 Searching all clickable elements...")
                    all_clickable = driver.find_elements(By.XPATH, "//*[@onclick or @href or self::button or self::a or self::input[@type='submit']]")
                    for elem in all_clickable:
                        try:
                            text = elem.text.strip() or elem.get_attribute("value") or ""
                            if "Send Comp" in text or "send comp" in text.lower():
                                submit_button = elem
                                print(f"    ✓ Found: <{elem.tag_name}> with text '{text}'")
                                break
                        except:
                            continue
                
                button_clicked = False
                
                if submit_button:
                    print("    🎯 CLICKING 'Send Comp Tickets'...")
                    
                    # Scroll into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                    time.sleep(0.3)
                    
                    # Highlight it
                    highlight_element(driver, submit_button, color="#FF6B6B", border=5, duration=0.5)
                    
                    # Try JavaScript click first (most reliable)
                    try:
                        driver.execute_script("arguments[0].click();", submit_button)
                        print("    ✅ JS click executed!")
                        button_clicked = True
                    except Exception as e:
                        print(f"    ⚠️  JS click failed: {e}")
                    
                    # Fallback: regular click
                    if not button_clicked:
                        try:
                            submit_button.click()
                            print("    ✅ Regular click executed!")
                            button_clicked = True
                        except Exception as e:
                            print(f"    ⚠️  Regular click failed: {e}")
                    
                    # Fallback: ActionChains
                    if not button_clicked:
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(driver).move_to_element(submit_button).click().perform()
                            print("    ✅ ActionChains click executed!")
                            button_clicked = True
                        except Exception as e:
                            print(f"    ⚠️  ActionChains failed: {e}")
                else:
                    print("    ❌ Could not find 'Send Comp Tickets' button!")
                    # Debug: list all elements that might be buttons
                    print("    📋 Debugging - all potential clickable elements:")
                    debug_elements = driver.find_elements(By.XPATH, "//button | //a[contains(@class, 'btn')] | //input[@type='submit']")
                    for i, elem in enumerate(debug_elements[:10]):  # limit to 10
                        try:
                            print(f"       {i}: <{elem.tag_name}> text='{elem.text.strip()}' class='{elem.get_attribute('class')}'")
                        except:
                            pass
                
                if not button_clicked:
                    print("    ❌ FAILED: Could not click the submit button!")
                    raise Exception("Submit button not found or not clickable")
                
                print(f"    ⏳ Waiting {delay}s for page to process...")
                time.sleep(delay)
                
                print(f"    ✅ SUCCESS: Sent {quantity} ticket(s) to {first_name} {last_name}")
                
                # IMPORTANT: Refresh the page to get a clean form for the next person
                # This ensures all fields (Ticket Type, Quantity) are present
                print("    🔄 Refreshing page for next submission...")
                driver.get(base_url)
                time.sleep(2)  # Wait for page to fully load
                successful += 1
                total_tickets += int(quantity)
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                print(f"    Error type: {type(e).__name__}")
                failed += 1
                
                # Screenshot on error
                try:
                    screenshot_name = f"error_{index}_{first_name}_{last_name}.png"
                    driver.save_screenshot(screenshot_name)
                    print(f"    📸 Screenshot saved: {screenshot_name}")
                except:
                    pass
                
                try:
                    print("    🔄 Attempting to recover...")
                    driver.get(base_url)
                    time.sleep(2)
                except:
                    pass
                
                cont = input("    Continue? (yes/skip/stop): ").strip().lower()
                if cont == 'stop':
                    break
                elif cont == 'skip':
                    continue
            
            total_processed += 1
            
            if total_processed % pause_every == 0 and total_processed < len(csv_reader):
                print(f"\n⏸️  PAUSED after {total_processed} submissions")
                print(f"   ✅ Success: {successful} | ❌ Failed: {failed} | 🎟️ Tickets: {total_tickets}")
                if input("   Continue? (yes/no): ").strip().lower() != 'yes':
                    break
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by Ctrl+C")
    
    finally:
        print("\n" + "="*60)
        print("📊 FINAL SUMMARY")
        print("="*60)
        print(f"   People processed: {total_processed}/{len(csv_reader)}")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   🎟️ Total tickets sent: {total_tickets}")
        print("="*60)


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=./chrome_session")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://ticketbud.com/admin/events/7f49895a-f629-11f0-9117-42010a7170e9/orders/comps/new")
        
        input("Press Enter after logging in (only needed first time)...")
        
        csv_file = "Ticket.csv"
        ticket_type = "General"
        
        send_comp_tickets_from_csv(
            driver=driver,
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