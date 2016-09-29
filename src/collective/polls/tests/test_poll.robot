*** Settings ***

Resource  collective/cover/tests/cover.robot
Variables  plone/app/testing/interfaces.py
Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open Test Browser
Test Teardown  Close all browsers

*** Variables ***

${link_placeholder}  a#collective-polls-poll
${title_selector}  input#form-widgets-IBasic-title
${description_selector}  textarea#form-widgets-IBasic-description
${option_placeholder}  textarea.task-description
${folder_link_placeholder}  a#folder
${folder_title_selector}  input#title
${polls_tile_location}  'collective.polls'
${tile_selector}  div.tile-container div.tile
${poll_selector}  .ui-draggable .contenttype-collective-polls-poll

*** Test cases ***

Test CRUD
    Enable Autologin as  Site Administrator
    Go to Homepage

    Create Poll  My poll  This is a test
    Update  My poll fixed  This is a fixed test
    Delete

Test Poll in Private Folder
    Enable Autologin as  Site Administrator
    Go to Homepage

    Add Poll in Private Folder  Test Folder  Test Poll

Test Poll in Public Folder
    Enable Autologin as  Site Administrator
    Go to Homepage

    Add Poll in Public Folder  Test Folder  Test Poll

Test portlet poll
    Enable Autologin as  Site Administrator
    Go to Homepage

    Add Poll in Public Folder  Test Folder  Test Poll
    Go to  ${PLONE_URL}/@@manage-portlets
    Select From List By Label  css=#portletmanager-plone-rightcolumn select[name=":action"]  Voting portlet
    Input text  id=form.header  Latest poll!
    Select From List By Label  id=form.poll  Latest opened poll
    Click Button  Save
    Goto Homepage
    Page Should Contain  Latest poll
    Page Should Contain Element  css=#portal-column-two dl.votePortlet h3 a[href$="test-poll"]
    Go to  ${PLONE_URL}/@@manage-portlets
    Click Element  link=Voting portlet
    Unselect Checkbox  name=form.link_poll
    Click Button  Save
    Goto Homepage
    Page Should Contain  Latest poll
    Page Should Not Contain Element  css=#portal-column-two dl.votePortlet h3 a[href$="test-poll"]
    Page Should Contain Element  css=#portal-column-two dl.votePortlet h3

Test tile poll
    Enable Autologin as  Site Administrator
    Go to Homepage

    Add Poll in Public Folder  Test Folder  Test Poll
    Go to Homepage

    Create Cover  Title  Description  Empty layout

    # add a poll tile to the layout
    Open Layout Tab
    Add Tile  ${polls_tile_location}
    Save Cover Layout

    # as tile is empty, we see default message
    Compose Cover
    Page Should Contain  Poll Tile

    # populate tile
    Open Content Chooser
    Click Element  link=Content tree
    Click Element  css=.ui-draggable a[href*=test-folder]
    Drag And Drop  css=${poll_selector}  css=${tile_selector}
    Wait Until Page Contains Element  css=div.poll-tile.vote-container

    # move to the default view and check tile persisted
    Click Link  link=View
    Page Should Contain Element  css=div.poll-tile.vote-container

    # select a poll and check if there is a bar chart
    Click Element  css=input[type="radio"][value="1"]
    Click Element  css=input[name="poll.submit"]
    Wait Until Page Contains Element  css=div.poll-data.bar-poll

# Robot Framework can't see the cookie information
# May be related to: https://github.com/robotframework/Selenium2Library/issues/273
Test poll workflow
    Enable Autologin as  Site Administrator
    Go to Homepage

    Add Poll in Public Folder  Test Folder  Test Poll

    # select a poll and check if there is a bar chart
    Click Element  css=input[type="radio"][value="1"]
    Click Element  css=input[name="poll.submit"]
    Wait Until Page Contains Element  css=div.poll-data.bar-poll

    Workflow Reject
    Wait Until Page Contains  Available options:
    Element Should Not Be Visible  css=input[name="poll.submit"]

    Workflow Open
    Click Element  css=input[type="radio"][value="1"]
    Click Element  css=input[name="poll.submit"]
    Wait Until Page Contains Element  css=div.poll-data.bar-poll

    Workflow Close
    Wait Until Page Contains Element  css=div.poll-data.bar-poll


*** Keywords ***

Add Option
    [Arguments]  ${option}

    Input Text  css=${option_placeholder}  ${option}
    Click Button  Add
    Wait Until Page Contains  ${option}

Remove Option
    [Documentation]  Should remove the named option; but I don't know how to
    ...              do it so we are removing the first option only for now
    [Arguments]  ${option}

    Click Link  Delete Option
    # XXX: why this is not working?
    #Page Should Not Contain  Maybe


Create Poll
    [arguments]  ${title}  ${description}

    Open Add New Menu
    Click Link  css=${link_placeholder}
    Page Should Contain  Add Poll
    Page Should Contain  Allow anonymous
    Input Text  css=${title_selector}  ${title}
    Input Text  css=${description_selector}  ${description}
    Add Option  Maybe
    Add Option  Yes
    Add Option  No
    Click Button  Save
    Page Should Contain  Item created

Update
    [arguments]  ${title}  ${description}

    Click Link  link=Edit
    Page Should Contain  Edit Poll
    Input Text  css=${title_selector}  ${title}
    Input Text  css=${description_selector}  ${description}
    Remove Option  Maybe
    Click Button  Save
    Page Should Contain  Changes saved
    Page Should Not Contain  Maybe

Delete
    Open Action Menu
    Click Link  css=a#plone-contentmenu-actions-delete
    Click Button  Delete
    Page Should Contain  Plone site

Create Folder
    [arguments]  ${title}

    Open Add New Menu
    Click Link  css=${folder_link_placeholder}
    #Page Should Contain  Add Folder
    Input Text  css=${folder_title_selector}  ${title}
    Click Button  Save
    Page Should Contain  Changes saved.

Workflow Open
    Trigger Workflow Transition  open

Workflow Reject
    Trigger Workflow Transition  reject

Workflow Close
    Trigger Workflow Transition  close

Add Poll in Private Folder
    [arguments]  ${folder_title}  ${poll_title}
    Create Folder  ${folder_title}
    Create Poll  ${poll_title}  This is a test
    Workflow Open
    Page Should Contain  Anonymous user won't be able to vote, you forgot to publish the parent folder, you must sent back the poll to private state, publish the parent folder and open the poll again

Add Poll in Public Folder
    [arguments]  ${folder_title}  ${poll_title}
    Create Folder  ${folder_title}
    Workflow Publish
    Create Poll  ${poll_title}  This is a test
    Workflow Open
    Page Should Not Contain  Anonymous user won't be able to vote, you forgot to publish the parent folder, you must sent back the poll to private state, publish the parent folder and open the poll again
