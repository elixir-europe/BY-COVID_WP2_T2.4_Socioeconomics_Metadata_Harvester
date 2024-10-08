
# BY-COVID WP2 T2.4 Metadata harvester and transformer

Implements the harvesting and transformation of socio-economic metadata for COVID-19 Data Portal. Work was done as a part of BY-COVID project Work Package 2 Task 2.4 and funded from Horizon Europe programme.

## Harvesting

Harvesting tool has been implemented with the use and extension of the open-source software DSpace for the collection, processing, retrieving, searching, and browsing of the harvested metadata records. It can be customised to support different metadata schemes and different content providers. The basic protocol used for the harvesting process is OAI-PMH. The harvesting tool has been extended with a set of endpoints that allow for the search and retrieval of the metadata records programmatically based on specific business needs, including the consumption of the metadata records to the COVID-19 Data Portal. The API is based on Open API principles (RESTful) and provides JSON responses.

## XML Transformation

XML transformation is done with a Python app (by-covid-xml-transformer) that uses the previously mentioned extended DSpace endpoints with query ‘COVID’ to get a list of records to harvest and link to where they can be harvested from. Those records are then harvested, processed (e.g. HTML tags removed) and transformed into extended OmicsDI format supported by the COVID-19 Data Portal. Transformation supports metadata that is in Dublin Core, DDI-Codebook 2.5 or DataCite format. The result is one XML file for every source. Those files are validated against OmicsDI schema and also validated to be valid XML before being publicly available for the portal to retrieve and use.

# DSpace

[![Build Status](https://travis-ci.org/DSpace/DSpace.png?branch=master)](https://travis-ci.org/DSpace/DSpace)

[DSpace Documentation](https://wiki.duraspace.org/display/DSDOC/) | 
[DSpace Releases](https://github.com/DSpace/DSpace/releases) |
[DSpace Wiki](https://wiki.duraspace.org/display/DSPACE/Home) | 
[Support](https://wiki.duraspace.org/display/DSPACE/Support)

DSpace open source software is a turnkey repository application used by more than 
1000+ organizations and institutions worldwide to provide durable access to digital resources.
For more information, visit http://www.dspace.org/

## Downloads

The latest release of DSpace can be downloaded from the [DSpace website](http://www.dspace.org/latest-release/) or from [GitHub](https://github.com/DSpace/DSpace/releases).

Past releases are all available via GitHub at https://github.com/DSpace/DSpace/releases

## Documentation / Installation

Documentation for each release may be viewed online or downloaded via our [Documentation Wiki](https://wiki.duraspace.org/display/DSDOC/). 

The latest DSpace Installation instructions are available at:
https://wiki.duraspace.org/display/DSDOC6x/Installing+DSpace

Please be aware that, as a Java web application, DSpace requires a database (PostgreSQL or Oracle) 
and a servlet container (usually Tomcat) in order to function.
More information about these and all other prerequisites can be found in the Installation instructions above.

## Contributing

DSpace is a community built and supported project. We do not have a centralized development or support team, 
but have a dedicated group of volunteers who help us improve the software, documentation, resources, etc.

We welcome contributions of any type. Here's a few basic guides that provide suggestions for contributing to DSpace:
* [How to Contribute to DSpace](https://wiki.duraspace.org/display/DSPACE/How+to+Contribute+to+DSpace): How to contribute in general (via code, documentation, bug reports, expertise, etc)
* [Code Contribution Guidelines](https://wiki.duraspace.org/display/DSPACE/Code+Contribution+Guidelines): How to give back code or contribute features, bug fixes, etc.
* [DSpace Community Advisory Team (DCAT)](https://wiki.duraspace.org/display/cmtygp/DSpace+Community+Advisory+Team): If you are not a developer, we also have an interest group specifically for repository managers. The DCAT group meets virtually, once a month, and sends open invitations to join their meetings via the [DCAT mailing list](https://groups.google.com/d/forum/DSpaceCommunityAdvisoryTeam).

We also encourage GitHub Pull Requests (PRs) at any time. Please see our [Development with Git](https://wiki.duraspace.org/display/DSPACE/Development+with+Git) guide for more info.

In addition, a listing of all known contributors to DSpace software can be
found online at: https://wiki.duraspace.org/display/DSPACE/DSpaceContributors

## Getting Help

DSpace provides public mailing lists where you can post questions or raise topics for discussion.
We welcome everyone to participate in these lists:

* [dspace-community@googlegroups.com](https://groups.google.com/d/forum/dspace-community) : General discussion about DSpace platform, announcements, sharing of best practices
* [dspace-tech@googlegroups.com](https://groups.google.com/d/forum/dspace-tech) : Technical support mailing list. See also our guide for [How to troubleshoot an error](https://wiki.duraspace.org/display/DSPACE/Troubleshoot+an+error).
* [dspace-devel@googlegroups.com](https://groups.google.com/d/forum/dspace-devel) : Developers / Development mailing list

Additional support options are listed at https://wiki.duraspace.org/display/DSPACE/Support

DSpace also has an active service provider network. If you'd rather hire a service provider to 
install, upgrade, customize or host DSpace, then we recommend getting in touch with one of our 
[Registered Service Providers](http://www.dspace.org/service-providers).

## Issue Tracker

The DSpace Issue Tracker can be found at: https://jira.duraspace.org/projects/DS/summary

## License

DSpace source code is freely available under a standard [BSD 3-Clause license](https://opensource.org/licenses/BSD-3-Clause).
The full license is available at http://www.dspace.org/license/
