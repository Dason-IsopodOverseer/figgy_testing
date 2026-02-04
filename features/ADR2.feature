Feature: ADR 2
  We want to ensure the decision specified
  in this record is enforced

  Scenario: Check If Sidekiq Exists
    Given we are using a Ruby framework called Sidekiq 
    When we read our Gemfile
    Then Sidekiq will be listed as a dependency
  
  Scenario: Check If Sidekiq Queues Are Listed
    Given we are using queues of three different priorities
    When we read our health checker utility script
    Then default will be listed as a queue to check
    And low will be listed as a queue to check
    And super_low will be listed as a queue to check

  Scenario: Check If Sidekiq Queues Exist in Production
    Given we are using queues of three different priorities
    Given Sidekiq Queues Are Listed
    When we run our health checker utility script
    Then our health checker utility script will pass