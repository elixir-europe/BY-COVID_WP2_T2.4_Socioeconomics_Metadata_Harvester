<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:xml="http://www.w3.org/XML/1998/namespace"
xmlns:meta="transformation:metadata"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:oai="http://schema.datacite.org/oai/oai-1.1/"
xsi:schemaLocation="http://schema.datacite.org/oai/oai-1.1/ http://schema.datacite.org/oai/oai-1.1/oai.xsd"
version="2.0"
xpath-default-namespace="http://datacite.org/schema/kernel-4"
exclude-result-prefixes="#all">

    <meta:metadata>
        <identifier>datacite-to-omicsdi</identifier>
        <title>DataCite to OmicsDI</title>
        <description>Convert DataCite to OmicsDI format</description>
        <outputFormat>XML</outputFormat>
        <parameters>
            <parameter name="entry_id" format="xs:string" description="Unique entry id for each dataset metadata"/>
        </parameters>
    </meta:metadata>

    <xsl:param name="entry_id">{$entry_id}</xsl:param>

    <xsl:output indent="yes" omit-xml-declaration="yes" />

    <xsl:template match="oai:oai_datacite">
        <entry id="{$entry_id}">
            <!-- M, name -->
            <name>
                <xsl:value-of select="oai:payload/resource/titles/title/text()" />
            </name>
            <!-- M, description -->
            <description>
                <xsl:value-of select="oai:payload/resource/descriptions/description/text()" />
            </description>
            <dates>
                <!-- M, publication -->
                <date>
                    <xsl:attribute name="type">publication</xsl:attribute>
                    <xsl:attribute name="value">
                        <xsl:choose>
                            <xsl:when test="oai:payload/resource/dates/date[@dateType='Issued']">
                                <xsl:value-of select="meta:getByDateType(oai:payload/resource/dates/date, 'Issued')"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="oai:payload/resource/publicationYear/text()"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </date>
                <!-- M, updated -->
                <date>
                    <xsl:attribute name="type">updated</xsl:attribute>
                    <xsl:attribute name="value">
                        <xsl:choose>
                            <xsl:when test="oai:payload/resource/dates/date[@dateType='Updated']">
                                <xsl:value-of select="meta:getByDateType(oai:payload/resource/dates/date, 'Updated')"/>
                            </xsl:when>
                            <xsl:when test="oai:payload/resource/dates/date[@dateType='Issued']">
                                <xsl:value-of select="meta:getByDateType(oai:payload/resource/dates/date, 'Issued')"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="oai:payload/resource/publicationYear/text()"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </date>
                <!-- A, collection_single_date -->
                <!-- A, collection_start_date -->
                <!-- A, collection_end_date -->
            </dates>
            <additional_fields>
                <!-- M, full_dataset_link -->
                <field name="full_dataset_link">
                    <xsl:value-of select="oai:payload/resource/alternateIdentifiers/alternateIdentifier[@alternateIdentifierType='URL'][1]/text()" />
                </field>
                <!-- M, repository -->
                <field name="repository">
                    <xsl:value-of select="oai:payload/resource/publisher/text()" />
                </field>
                <!-- A, sample_protocol -->
                <!-- A, analysis_unit -->
                <!-- A, spatial_coverage -->
                <xsl:copy-of select="meta:getEach('spatial_coverage', oai:payload/resource/geoLocations/geoLocation/geoLocationPlace)" />
                <!-- A, temporal_coverage -->
                <xsl:if test="oai:payload/resource/dates/date[@dateInformation='Temporal Coverage']">
                    <field name="temporal_coverage">
                        <xsl:value-of select="oai:payload/resource/dates/date[@dateInformation='Temporal Coverage']/text()"/>
                    </field>
                </xsl:if>
                <!-- A, persistent_identifier -->
                <!-- A, persistent_identifier_type -->
                <!-- A, data_access -->
                <!-- A, universe_included -->
                <!-- A, universe_excluded -->
                <!-- A, collection_mode -->
                <!-- A, time_method -->
                <!-- A, author -->
                <!-- A, author_affiliation -->
                <xsl:for-each select="oai:payload/resource/creators/creator">
                    <field name="author">
                        <xsl:value-of select="creatorName/text()" />
                    </field>
                    <xsl:if test="affiliation">
                        <field name="author_affiliation">
                            <xsl:value-of select="affiliation/text()" />
                        </field>
                    </xsl:if>
                </xsl:for-each>
                <!-- A, license -->
                <xsl:for-each select="oai:payload/resource/rightsList/rights">
                    <field name="license">
                        <xsl:value-of select="text(),@rightsURI" separator=", " />
                    </field>
                </xsl:for-each>
                <!-- A, keywords -->
                <xsl:if test="oai:payload/resource/subjects/subject">
                    <field name="keywords">
                        <xsl:value-of select="oai:payload/resource/subjects/subject" separator="; " />
                    </field>
                </xsl:if>
            </additional_fields>
        </entry>
    </xsl:template>

    <xsl:function name="meta:getEach">
        <xsl:param name="fieldname" />
        <xsl:param name="element" />
        <xsl:for-each select="$element">
            <field name="{$fieldname}">
                <xsl:value-of select="text()"/>
            </field>
        </xsl:for-each>
    </xsl:function>
    <xsl:function name="meta:getByDateType">
        <xsl:param name="element" />
        <xsl:param name="attribute" />
        <xsl:for-each select="$element">
            <xsl:choose>
                <xsl:when test="@dateType=$attribute">
                    <xsl:value-of select="text()" />
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
    </xsl:function>
</xsl:stylesheet>