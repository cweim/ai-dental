# AI Dentist Frontend Test Scenarios

This document contains comprehensive frontend test scenarios written in Cucumber/BDD style for the AI Dentist booking system.

## Feature: Homepage Navigation and Display

### Scenario: User visits the homepage
```
Given I am a user visiting the dental practice website
When I navigate to "http://localhost:3000"
Then I should see the homepage load completely
And I should see the dental practice branding/logo
And I should see a navigation menu
And I should see a "Book Appointment" call-to-action button
And the page should be responsive on different screen sizes
```

### Scenario: User navigates through the site
```
Given I am on the homepage
When I click on navigation menu items
Then each link should navigate to the correct page
And I should be able to return to the homepage
And all navigation should work smoothly
```

### Scenario: User tests responsive design
```
Given I am on any page of the website
When I resize my browser window to mobile size
Then the layout should adapt to the smaller screen
And all content should remain accessible
And the navigation menu should collapse to a hamburger menu
And text should remain readable
```

## Feature: Appointment Booking

### Scenario: User accesses booking form
```
Given I am on the homepage
When I click the "Book Appointment" button
Then I should be redirected to the appointments page
And I should see a booking form with all required fields
And the form should appear clean and professional
```

### Scenario: User selects treatment type
```
Given I am on the appointments booking page
When I look for treatment type selection
And I click on the treatment dropdown/selector
Then I should see available treatment options including:
  | Treatment Type |
  | Dental Cleaning |
  | Filling |
  | Extraction |
  | Checkup |
  | Whitening |
  | Orthodontic |
When I select "Dental Cleaning"
Then I should see treatment-specific information displayed
And the price and duration should be shown
```

### Scenario: User selects appointment date
```
Given I am on the booking form
When I click on the date picker field
Then a calendar widget should open
And past dates should be disabled or not selectable
When I select a future date
Then the date should be accepted
And available time slots should appear for that date
```

### Scenario: User selects appointment time
```
Given I have selected a valid future date
When I look at the available time slots
Then I should see a list of available appointment times
When I click on an available time slot
Then the time should be selected
And the time should be highlighted or marked as selected
```

### Scenario: User fills patient information with valid data
```
Given I am on the booking form
When I enter the following information:
  | Field | Value |
  | Name | John Doe |
  | Email | john.doe@email.com |
  | Phone | +1234567890 |
  | Notes | First visit, no allergies |
And I have selected a treatment, date, and time
When I click the "Submit" or "Book Appointment" button
Then the form should submit successfully
And I should see a loading indicator
And I should receive a success confirmation message
And I should see my appointment details displayed
```

### Scenario: User submits form with missing required fields
```
Given I am on the booking form
When I leave the name field empty
And I click submit
Then I should see a validation error for the name field
And the form should not submit
And I should see a clear error message
```

### Scenario: User enters invalid email format
```
Given I am on the booking form
When I enter "invalid-email" in the email field
And I click submit
Then I should see an email format validation error
And the form should not submit
And I should see a helpful error message about email format
```

### Scenario: User tries to select past date
```
Given I am on the booking form
When I click on the date picker
And I try to select yesterday's date
Then the past date should be disabled
And I should not be able to select it
```

### Scenario: User receives booking confirmation
```
Given I have successfully submitted a booking
When I check my email inbox
Then I should receive a confirmation email within 5 minutes
And the email should contain all my appointment details
And the email should include the practice contact information
And the email should look professional
```

## Feature: Admin Dashboard

### Scenario: User accesses admin dashboard
```
Given I am an admin user
When I navigate to "http://localhost:3000/admin"
Then I should see the admin dashboard load
And I should see practice statistics displayed
And I should see navigation options for different admin sections
```

### Scenario: User views dashboard statistics
```
Given I am on the admin dashboard
Then I should see statistics cards showing:
  | Statistic | Description |
  | Total Appointments | Count of all appointments |
  | Today's Appointments | Count of today's appointments |
  | Revenue Information | Total revenue calculations |
  | Pending Appointments | Count of pending appointments |
And the numbers should reflect current data
And the statistics should update when new appointments are made
```

### Scenario: User navigates between admin sections
```
Given I am on the admin dashboard
When I click on "Calendar" navigation
Then I should be taken to the calendar view
When I click on "Sheets" navigation
Then I should be taken to the sheets view
When I click on "QA Editor" navigation
Then I should be taken to the QA management page
When I click on "Chatbot Tester" navigation
Then I should be taken to the chatbot testing interface
And I should be able to navigate back to dashboard from any section
```

## Feature: Calendar Management

### Scenario: User views appointment calendar
```
Given I am on the admin calendar page
When the calendar loads
Then I should see a calendar interface (month/week/day view)
And I should see booked appointments displayed on the calendar
And appointments should appear on the correct dates and times
And the calendar should be interactive and responsive
```

### Scenario: User clicks on appointment in calendar
```
Given I am viewing the calendar with appointments
When I click on a booked appointment
Then I should see appointment details in a popup or modal
And I should see patient information displayed
And I should see treatment details
And I should see action buttons for managing the appointment
```

### Scenario: User changes appointment status
```
Given I have opened an appointment's details
When I look for status change options
Then I should see status options like:
  | Status |
  | Confirmed |
  | Pending |
  | Completed |
  | Cancelled |
When I select "Confirmed"
Then the appointment status should update
And the change should be saved immediately
And the calendar should reflect the status change
```

### Scenario: User cancels an appointment
```
Given I have opened an appointment's details
When I click the "Cancel" option
Then I should see a confirmation dialog
When I confirm the cancellation
Then the appointment status should change to "Cancelled"
And the appointment should be visually marked as cancelled
And the change should persist when I refresh the page
```

## Feature: Google Sheets Integration

### Scenario: User views sheets data
```
Given I am on the admin sheets page
When the page loads
Then I should see appointment data from Google Sheets
And the data should be displayed in a clear tabular format
And the data should match what I see in the calendar
And dates, times, and prices should be properly formatted
```

### Scenario: User refreshes sheets data
```
Given I am viewing the sheets page
When I book a new appointment through the frontend
And I return to the sheets page
And I refresh or reload the data
Then the new appointment should appear in the sheets data
And all fields should be populated correctly
```

## Feature: QA Management System

### Scenario: User accesses QA editor
```
Given I am on the admin QA editor page
When the page loads
Then I should see a clean interface for managing Q&A pairs
And I should see existing Q&A pairs displayed
And I should see an option to add new Q&A pairs
```

### Scenario: User creates new QA pair
```
Given I am on the QA editor page
When I click "Add New" or "Create Q&A" button
Then I should see a form for creating new Q&A
When I fill in:
  | Field | Value |
  | Question | What should I bring to my appointment? |
  | Answer | Please bring your insurance card, ID, and a list of current medications |
  | Category | appointments |
And I click save
Then the new Q&A pair should be created
And it should appear in the Q&A list immediately
```

### Scenario: User edits existing QA pair
```
Given I am viewing the list of Q&A pairs
When I select an existing Q&A pair
And I click edit or modify
Then I should see an edit form with current content
When I change the answer text
And I save the changes
Then the Q&A pair should be updated
And the changes should be visible immediately
```

### Scenario: User deletes QA pair
```
Given I am viewing a Q&A pair
When I click the delete option
Then I should see a confirmation prompt
When I confirm the deletion
Then the Q&A pair should be removed from the list
And it should no longer appear in the interface
```

### Scenario: User searches QA pairs
```
Given I am on the QA editor page with multiple Q&A pairs
When I use the search functionality
And I search for "appointment"
Then I should see only Q&A pairs containing "appointment"
When I clear the search
Then all Q&A pairs should be visible again
```

## Feature: Chatbot Testing

### Scenario: User accesses chatbot tester
```
Given I am on the admin chatbot tester page
When the page loads
Then I should see a chat interface similar to messaging apps
And I should see an input field for typing messages
And I should see a chat history area
And the interface should look professional
```

### Scenario: User asks basic dental questions
```
Given I am in the chatbot tester
When I type "What are your office hours?"
And I send the message
Then I should receive a response within reasonable time
And the response should be relevant and helpful
When I ask "How much does a cleaning cost?"
Then I should receive pricing information
When I ask "What treatments do you offer?"
Then I should receive a list of available treatments
```

### Scenario: User asks appointment-related questions
```
Given I am chatting with the bot
When I ask "How do I book an appointment?"
Then I should receive step-by-step booking instructions
When I ask "What should I bring to my appointment?"
Then I should receive a list of items to bring
When I ask "Can I reschedule my appointment?"
Then I should receive information about rescheduling policies
```

### Scenario: User asks treatment information questions
```
Given I am using the chatbot
When I ask "Tell me about dental cleanings"
Then I should receive detailed information about cleanings
When I ask "How long does a filling take?"
Then I should receive duration information
When I ask "What's the difference between cleaning and deep cleaning?"
Then I should receive a clear explanation of the differences
```

### Scenario: User views chatbot response sources
```
Given I have received a response from the chatbot
When I look at the response
Then I should see source citations or references
And the sources should be relevant to the question asked
And source attribution should be clear and helpful
```

## Feature: End-to-End Integration

### Scenario: Complete booking workflow
```
Given I am a new patient visiting the website
When I navigate through the complete booking process:
  - Visit homepage
  - Click book appointment
  - Select treatment type
  - Choose date and time
  - Fill patient information
  - Submit booking
Then I should receive confirmation
When I check the admin calendar
Then my appointment should appear there
When I check the sheets view
Then my appointment should appear in the sheets data
When I check my email
Then I should receive a confirmation email
```

### Scenario: Data consistency across systems
```
Given I have booked multiple appointments with different treatments
When I check the admin calendar
Then all appointments should appear correctly
When I check the Google Sheets view
Then all appointment data should match the calendar
When I check my email confirmations
Then all details should match across all systems
And no information should be lost or corrupted
```

## Feature: Error Handling and Edge Cases

### Scenario: User experiences network connectivity issues
```
Given I am filling out the booking form
When I disconnect my internet connection
And I try to submit the form
Then I should see an appropriate error message about network issues
When I reconnect to the internet
And I try to submit again
Then the form should work normally
```

### Scenario: User enters extreme input values
```
Given I am on the booking form
When I enter a very long name (100+ characters)
Then the system should handle it gracefully
When I enter special characters in the name field
Then the system should either accept them or show clear validation
When I try to book an appointment for a date 2 years in the future
Then the system should either accept it or explain date limitations
```

### Scenario: User tests browser compatibility
```
Given I am using Chrome browser
When I test all booking functionality
Then everything should work properly
Given I switch to Firefox browser
When I test the same functionality
Then it should work consistently
Given I use Safari browser
When I test the functionality
Then there should be no major differences in behavior
```

## Feature: Mobile and Responsive Experience

### Scenario: User books appointment on mobile device
```
Given I am using a mobile device or mobile browser simulation
When I navigate to the booking page
Then the form should be easy to use on a small screen
When I fill out the booking form
Then all fields should work well with mobile keyboards
When I submit the booking
Then the process should complete successfully
And I should receive the same confirmation as on desktop
```

### Scenario: User accesses admin functions on mobile
```
Given I am using a mobile device
When I access the admin dashboard
Then the interface should adapt to the small screen
When I try to view the calendar
Then appointments should be readable and manageable
When I access the QA editor
Then I should be able to perform basic CRUD operations
And critical functionality should remain accessible
```

### Scenario: User tests touch interactions
```
Given I am on a touch-enabled device
When I interact with buttons and form elements
Then all touch interactions should work smoothly
When I scroll through content
Then scrolling should be smooth and responsive
When I zoom in and out
Then the layout should remain usable
```

## Acceptance Criteria Summary

### Must Work Scenarios:
- [ ] Homepage loads and displays correctly
- [ ] Complete appointment booking flow works end-to-end
- [ ] Form validation prevents invalid submissions
- [ ] Admin dashboard displays accurate statistics
- [ ] Calendar shows appointments correctly
- [ ] QA management allows full CRUD operations
- [ ] Chatbot responds relevantly to dental questions
- [ ] Email confirmations are received
- [ ] Data consistency across all systems
- [ ] Mobile experience is functional
- [ ] Error handling is graceful and user-friendly

### Performance Expectations:
- [ ] Pages load within 3 seconds
- [ ] Form submissions complete within 5 seconds
- [ ] Chatbot responses appear within 10 seconds
- [ ] Calendar navigation is smooth and responsive
- [ ] Mobile interactions feel natural and responsive

### User Experience Standards:
- [ ] All interfaces are intuitive and self-explanatory
- [ ] Error messages are helpful and actionable
- [ ] Success confirmations are clear and complete
- [ ] Navigation is consistent throughout the application
- [ ] Visual design is professional and trustworthy

---

**Testing Instructions:**
1. Start both frontend and backend servers
2. Use real email addresses for booking tests
3. Test each scenario step by step
4. Document any failures with screenshots
5. Test on multiple browsers and devices
6. Verify all data persistence and synchronization