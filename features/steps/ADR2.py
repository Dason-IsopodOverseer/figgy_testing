from behave import *
import os
import RubyChecks

@given('we are using a Ruby framework called Sidekiq')
def step_impl(context):
    pass

@when('we read our Gemfile')
def step_impl(context):
    # file directory primitives; current working directory
    cwd_root = os.path.join(os.getcwd(), "figgy")
    check = RubyChecks.RubyCheck(cwd_root, "Gemfile", "", "", "", "", ["sidekiq-pro"])
    assert check.result() is True

@then('Sidekiq will be listed as a dependency')
def step_impl(context):
    assert context.failed is False

# RUBY CHECKS
# import RubyChecks

# # file directory primitives; current working directory
# cwd_root = os.path.join(os.getcwd(), "alphagov_api-catalogue")
# check = RubyChecks.RubyCheck(cwd_root, ".ruby-version", "")
# check = RubyChecks.RubyCheck(cwd_root, ".ruby-version", "", "", "", "", ["rails", "sass", "puma"])
    
# # Perform the check
# print(f"   Finished Checking for Ruby\n   RESULT: {check.result()}")