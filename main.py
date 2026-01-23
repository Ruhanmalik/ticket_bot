import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def send_comp_tickets_from_csv(csv_file_path, ticket_type="General", delay = 3):
    """
    Automate sending comp tickets from a CSV file.
    
    Args:
        csv_file_path: Path to CSV file with columns: first_name, last_name, email
        ticket_type: The ticket type to select from dropdown (default: "General")
        delay: Delay between submissions in seconds (default: 2)
    """
    
    # Read CSV file
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        
        total_processed = 0
        successful = 0
        failed = 0
        
        for row in csv_reader:
            first_name = row['first_name'].strip()
            last_name = row['last_name'].strip()
            email = row['email'].strip()
            
            print(f"\n[{total_processed + 1}] Processing: {first_name} {last_name} ({email})")
            
            try:
                # Wait for form to be ready
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
                ticket_type_select = Select(driver.find_element(By.XPATH, "//select[contains(@class, 'ticket-type') or preceding-sibling::*[contains(text(), 'Ticket Type')]]"))
                ticket_type_select.select_by_visible_text(ticket_type)
                
                # Set Quantity to 1
                quantity_field = driver.find_element(By.XPATH, "//input[@type='number' or @value='1']")
                quantity_field.clear()
                quantity_field.send_keys("1")
                
                # Leave Comp Reason empty (clear it if it has any default value)
                comp_reason_field = driver.find_element(By.XPATH, "//input[@placeholder='Volunteer staff']")
                comp_reason_field.clear()
                
                # Ensure "Send tickets via email" checkbox is checked
                email_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
                if not email_checkbox.is_selected():
                    email_checkbox.click()
                
                # Click "Send Comp Tickets" button
                send_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Comp Tickets')]")
                send_button.click()
                
                # Wait for form to reset or success confirmation
                time.sleep(delay)
                
                print(f"    ✓ Successfully sent ticket to {first_name} {last_name}")
                successful += 1
                
            except Exception as e:
                print(f"    ✗ Error processing {first_name} {last_name}: {str(e)}")
                failed += 1
            
            total_processed += 1
        
        # Summary
        print("\n" + "="*60)
        print(f"SUMMARY:")
        print(f"Total processed: {total_processed}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print("="*60)

# Usage example:
if __name__ == "__main__":
    # Setup: Make sure you have Selenium and the appropriate WebDriver installed
    # pip install selenium
    
    # Initialize browser (uncomment and modify based on your browser)
    driver = webdriver.Chrome()  # or webdriver.Safari(), webdriver.Firefox()
    
    # Navigate to the comp tickets page
    # driver.get("https://ticketbud.com/admin/events/7f49895a-f629-11f0-9f17-42010a7170e9/orders/comps/new")
    # og one

    driver.get("https://ticketbud.com/admin/events/fe2e84b6-f627-11f0-bed6-42010a7170e9/orders/comps/new")
    # Wait for manual login if needed
    input("Press Enter after you've logged in and are on the comp tickets page...")
    
    # Run the automation
    csv_file = "test.csv"
    
    # Set your ticket type (must match exactly what's in the dropdown)
    ticket_type = "General"  # Change this to match your dropdown options
    
    # Run the script
    send_comp_tickets_from_csv(
        csv_file_path=csv_file,
        ticket_type=ticket_type,
        delay=3  # 3 seconds between submissions
    )
    
    print("\nAll tickets processed! Press Enter to close browser...")
    input()
    driver.quit()