External API

User Guide

Cardskipper – External API 2022-11-18

Page 2

1 INTRODUCTION ..................................................................................................................................................................... 3
2 GENERAL................................................................................................................................................................................ 3
2.1 RETRIEVE/SEND DATA ................................................................................................................................................................. 3
2.2 URLS....................................................................................................................................................................................... 3
2.3 SECURITY & AUTHENTICATION...................................................................................................................................................... 3
2.4 LANGUAGE SUPPORT................................................................................................................................................................... 3
3 RETRIEVE DATA...................................................................................................................................................................... 4
3.1 DOWNLOAD BASIC DATA.............................................................................................................................................................. 4
3.1.1 Countries........................................................................................................................................................................... 4
3.1.1.1 URL...............................................................................................................................................................................................4
3.1.2 Gender............................................................................................................................................................................... 4
3.1.2.1 URL...............................................................................................................................................................................................4
3.2 RETRIEVE ORGANISATIONS AND ROLES ............................................................................................................................................ 4
3.2.1 URL.................................................................................................................................................................................... 4
3.2.2 XML Schema...................................................................................................................................................................... 4
3.2.3 XML Data .......................................................................................................................................................................... 4
3.3 MEMBER SEARCH....................................................................................................................................................................... 4
3.3.1 URL.................................................................................................................................................................................... 4
3.3.2 XML Schema...................................................................................................................................................................... 4
3.3.3 XML Data .......................................................................................................................................................................... 4
3.3.4 XML Explination of Export of members............................................................................................................................. 5
4 SEND DATA ............................................................................................................................................................................ 6
4.1 IMPORT MEMBERS...................................................................................................................................................................... 6
4.1.1 URL.................................................................................................................................................................................... 6
4.1.2 XML Schema...................................................................................................................................................................... 6
4.1.3 XML Data .......................................................................................................................................................................... 6
4.1.4 XML Elements.................................................................................................................................................................... 6
4.1.4.1 Member.......................................................................................................................................................................................6
4.1.4.1.1 Member.Extra.........................................................................................................................................................................7
4.1.4.1.2 Member.Address ....................................................................................................................................................................7
4.1.4.1.3 Member.ContactInfo ..............................................................................................................................................................7
4.1.4.1.4 Member.Organisations...........................................................................................................................................................7
4.1.4.1.4.1 Member.Organisations.Organisation ..............................................................................................................................7
4.1.4.1.4.1.1 Member.Organisations.Organisation.Roles.Role.....................................................................................................8
4.1.4.1.4.1.2 Member.Organisations.Organisation.Tags.Tag .......................................................................................................8
4.2 SEND IMAGE.............................................................................................................................................................................. 8
4.2.1 URL.................................................................................................................................................................................... 8

Cardskipper – External API 2022-11-18

Page 3

1 Introduction
Cardskipper is a platform for digital membership cards and member communication. This document describes the
external API that can be used to retrieve and send data to the system.

2 General
2.1 Retrieve/Send data
The interface uses http-get and http-post, which means that you can download and submit data with a regular web
browser. The character encoding used is UTF8.
• http-get call functions return XML files with different parameters depending on function.
• http-post call functions will only accept XML files as input data.

2.2 URLs
https://api.cardskipper.se Production environment
https://api-test.cardskipper.se Test environment

The following is an example of complete call to test environment;
https://api-test.cardskipper.se/Organisation/Info
2.3 Security & Authentication
The communication is encrypted with SSL, with a valid server certificate.
As authentication method, "Basic Authentication" uses a username and password. The account that you log in with
should be a Cardskipper administrator account with API rights for the actual organisation.
Please note that each call requires the corresponding API access granted. If a specific call does not work, please send
an e-mail to support@cardskipper.se.
2.4 Language support
All requests support different languages with standard http header Accept-Language. For base data downloads, the
request will be in the specified language, and for the import base data information must be filed according to the
specified language.
If no language is specified, the default is English.

Cardskipper – External API 2022-11-18

Page 4

3 Retrieve data
All function calls use the http-get.
3.1 Download basic data
Retrieves basic data used by other functions
3.1.1 Countries
Retrieve available countries.
3.1.1.1 URL
No parameters used by this call. Path: /Basedata/Country/
3.1.2 Gender
Retrieve available genders.
3.1.2.1 URL
No parameters used by this call. Path: /Basedata/Gender/
3.2 Retrieve organisations and roles
Function to retrieve all organisations and roles where the user is authorised.
3.2.1 URL
No parameters used by this call. Path: /Organisation/Info/
3.2.2 XML Schema
The following scheme is used by this function: https://api.cardskipper.se/Doc/OrganisationInfo.xsd
3.2.3 XML Data
Example: https://api.cardskipper.se/Doc/OrganisationInfo.xml
3.3 Member search
Function to search for a member in all organisations and roles where the user is authorised.
3.3.1 URL
This function requires the posting of an XML. Please refer to section 3.3.3. Path: /Member/Export/
3.3.2 XML Schema
The following scheme is used by this function. Validate all XMLs sent with this scheme to handle data errors.
https://api.cardskipper.se/Doc/SearchCriteriaMember.xsd
3.3.3 XML Data
Example: https://api.cardskipper.se/Doc/SearchCriteriaMember.xml

Cardskipper – External API 2022-11-18

Page 5
3.3.4 XML Explination of Export of members
Only the search criteria that should contain values should be inluded (ie no criteria with an empty string should be
included), OrganisationId must be specified. Below you can see available search criteria.
XML Required Datatype Explination
MemberId No int Member number, Member id
OrganisationId Yes int Organisation number, Organisation id 3.2.1
RoleId No int Role Id. Must match Id from 3.2
UserId No int User number, User Id
OrganisationMemberId No long Membernumber on organisation
Birthdate No datetime Birthdate
Firstname No string Member firstname
Lastname No string Member lastname
Cellphone No string Mobile number
Recommended formatting
Swedish mobile number : 070 111 222
Foreign mobile number: +45 70 111 222

TagContains No string Search labels
OrganisationUnit No string Organisation unit
HasUserDevice No bool Has logged in user
OnlyActive No bool Active users
ChangedAt Nej datetime Members with changes after a certain date.

Cardskipper – External API 2022-11-18

Page 6

4 Send data
All function calls are using http-post.
4.1 Import members
Function for importing members into organisations and roles. All imports will be logged and accessible at
https://adm.cardskipper.se. Please see refer to Membership-Imports in the Administration Guide for Cardskipper.
4.1.1 URL
This function requires the posting of an XML. Please refer to section 4.1.3. Path: /Import/Member/
4.1.2 XML Schema
The following scheme is used by this function. Validate all XMLs sent with this scheme to handle data errors.
https://api.cardskipper.se/Doc/MemberImport.xsd
4.1.3 XML Data
Example: https://api.cardskipper.se/Doc/MemberImport.xml
4.1.4 XML Elements
4.1.4.1 Member
XML Required Datatype Explination
OrganisationMemberId Yes long Member Id
Lastname Yes string Lastname
Firstname Yes string Firstname
Birthdate Yes datetime Birtdate
Birthnumber No string Birth number
GenderCode No string Gender. Valid Id, Code or Name from

3.1.2 required

Nationality No string Nationality. Valid Id, Code, Shortname,
Iso or Localname from 3.1.1 required
Inactive Yes bool Inactivates member and memberships.

Cardskipper – External API 2022-11-18

Page 7

4.1.4.1.1 Member.Extra
XML Required Datatype Explination
Extra1 No string Extra can be used as own parameters eg

”Place of birth”.

Extra2 No string
Extra3 Np string

4.1.4.1.2 Member.Address
XML Required Datatype Explination
Line1 No string Address
Line2 No string Address
Zip No string Zipcode
City No string City

4.1.4.1.3 Member.ContactInfo
XML Required Datatype Explination
CellPhone1 * string Mobile phone number 1
Format: +44 70 111 222
CellPhone2 No string Mobile phone number 2
Format: +44 70 111 222

EMail * string E-mail
* = Mobile phone number 1 or Email is required.
4.1.4.1.4 Member.Organisations
4.1.4.1.4.1 Member.Organisations.Organisation
XML Required Datatype Explination
Id Yes int Organisation Id. Valid Id from 3.2

required

ClearTags Yes bool Removes all search labels for the

member.

Cardskipper – External API 2022-11-18

Page 8
4.1.4.1.4.1.1 Member.Organisations.Organisation.Roles.Role
XML Required Datatype Explination
Id Yes int Role Id. Valid Id from 3.2 required
StartDate Yes datetime Membership valid from
EndDate Yes datetime Membership valid to
Type No string Member Type
OrganisationUnit No string Organisation Unit

4.1.4.1.4.1.2 Member.Organisations.Organisation.Tags.Tag
XML Required Datatype Explination
Label No string Search label(s)

4.2 Send image
Function for importing a member image (photo).
4.2.1 URL
Parameter OrganisationId (Please refer to section Retrieve Organisations) and OrganisationMemberId (Please refer to
sections Member search/Import members).
Path: /MemberBlob/Blob/{OrganisationId}/{OrganisationMemberId} (POST).
Use Content-Disposition – FileName otherwise resonse will be 400 (type Content-Disposition = inline; filename="Donald duck.jpg")