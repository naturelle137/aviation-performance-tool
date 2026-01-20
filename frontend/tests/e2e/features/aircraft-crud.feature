Feature: Aircraft CRUD Operations
  As a pilot
  I want to manage my aircraft profiles
  So that I can perform calculations for different aircraft

  Background:
    Given I am on the aircraft page

  @critical
  Scenario: Create a new aircraft
    When I click the "Add Aircraft" button
    And I fill in the aircraft form with:
      | Field        | Value    |
      | Registration | D-TEST   |
      | Manufacturer | Cessna   |
      | Type         | C172S    |
      | MTOW         | 1157     |
      | Empty Weight | 743      |
      | Empty Arm    | 2.35     |
      | Fuel Capacity| 200      |
      | Fuel Arm     | 2.40     |
    And I click "Save"
    Then I should see "D-TEST" in the aircraft list
    And I should see a success message "Aircraft D-TEST created"

  @critical
  Scenario: View aircraft details
    Given I have an aircraft "D-EABC" registered
    When I click on "D-EABC" in the aircraft list
    Then I should see the aircraft detail page
    And I should see the registration "D-EABC"
    And I should see the weight data section

  Scenario: Delete an aircraft
    Given I have an aircraft "D-DELETE" registered
    When I click the delete button for "D-DELETE"
    And I confirm the deletion
    Then "D-DELETE" should not appear in the aircraft list
    And I should see a success message "Aircraft D-DELETE deleted"

  Scenario: Prevent duplicate registration
    Given I have an aircraft "D-EXIST" registered
    When I try to create another aircraft with registration "D-EXIST"
    Then I should see an error message "already exists"
