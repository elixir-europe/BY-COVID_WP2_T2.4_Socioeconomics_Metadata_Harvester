<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:xml="http://www.w3.org/XML/1998/namespace"
xmlns:meta="transformation:metadata"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:dcterms="http://purl.org/dc/terms/1.1"
xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
version="2.0"
exclude-result-prefixes="#all">

    <meta:metadata>
        <identifier>dc-to-omicsdi</identifier>
        <title>Dublin Core to OmicsDI</title>
        <description>Convert Dublin Core to OmicsDI format</description>
        <outputFormat>XML</outputFormat>
        <parameters>
            <parameter name="entry_id" format="xs:string" description="Unique entry id for each dataset metadata"/>
        </parameters>
    </meta:metadata>

    <xsl:param name="entry_id">{$entry_id}</xsl:param>

    <xsl:output indent="yes" omit-xml-declaration="yes" />

    <xsl:template match="oai_dc:dc">
        <entry id="{$entry_id}">
            <!-- M, name -->
            <name>
                <xsl:copy-of select="meta:getLangEn(dc:title)" />
            </name>
            <!-- M, description -->
            <description>
                <xsl:copy-of select="meta:getLangEn(dc:description)" />
            </description>
            <dates>
                <!-- M, publication -->
                <date>
                    <xsl:attribute name="type">publication</xsl:attribute>
                    <xsl:attribute name="value"><xsl:value-of select="meta:getLangEn(dc:date)"/></xsl:attribute>
                </date>
                <!-- M, updated -->
                <!-- Mandatory so set to be the as the same as publication since there doesn't seem to be anything better -->
                <date>
                    <xsl:attribute name="type">updated</xsl:attribute>
                    <xsl:attribute name="value"><xsl:value-of select="meta:getLangEn(dc:date)"/></xsl:attribute>
                </date>
                <!-- A, collection_single_date -->
                <!-- A, collection_start_date -->
                <!-- A, collection_end_date -->
            </dates>
            <additional_fields>
                <!-- M, full_dataset_link -->
                <field name="full_dataset_link">
                    <xsl:for-each select="dc:identifier[contains(text(),'http')][not(preceding-sibling::dc:identifier[contains(text(),'http')])]">
                        <xsl:value-of select="text()" />
                    </xsl:for-each>
                    <xsl:for-each select="dc:identifier[contains(text(),'10.5255/UKDA')][not(preceding-sibling::dc:identifier[contains(text(),'10.5255/UKDA')])]">http://doi.org/<xsl:value-of select="text()" /></xsl:for-each>
                </field>
                <!-- M, repository -->
                <field name="repository">
                    <!-- <xsl:copy-of select="meta:getLangEn(dc:publisher)" /> -->
                    <xsl:variable name="publisher" select="meta:getLangEn(dc:publisher)" />
                    <xsl:choose>
                        <xsl:when test="$publisher">
                            <xsl:value-of select="$publisher" />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:for-each select="dc:identifier[contains(text(),'UKDA')][not(preceding-sibling::dc:identifier[contains(text(),'UKDA')])]">UK Data Archive</xsl:for-each>
                            <xsl:for-each select="dc:identifier[contains(text(),'gesis')][not(preceding-sibling::dc:identifier[contains(text(),'gesis')])]">GESIS</xsl:for-each>
                        </xsl:otherwise>
                    </xsl:choose>
                </field>
                <!-- A, sample_protocol -->
                <!-- A, analysis_unit -->
                <!-- A, spatial_coverage -->
                <xsl:copy-of select="meta:getLangEnIfExists('spatial_coverage', dc:coverage)" />
                <!-- A, temporal_coverage -->
                <!-- A, persistent_identifier -->
                <!-- No idea how to find correct one when PID is just 10.4232/1.13880 for example -->
                <xsl:for-each select="dc:identifier[(contains(., 'urn') or contains(., 'ark') or contains(., 'handle') or contains(., 'doi')) and not(contains(., 'http'))][1]">
                    <field name="persistent_identifier">
                        <xsl:value-of select="text()" />
                    </field>
                </xsl:for-each>
                <!-- A, persistent_identifier_type -->
                <!-- Persistent identifier type cases one by one
                     No idea how to find correct one when PID is just 10.4232/1.13880 for example -->
                <xsl:for-each select="dc:identifier[contains(., 'urn')][1]">
                    <field name="persistent_identifier_type">
                        <xsl:value-of select="'URN'" />
                    </field>
                </xsl:for-each>
                <xsl:for-each select="dc:identifier[contains(., 'ark')][1]">
                    <field name="persistent_identifier_type">
                        <xsl:value-of select="'ARK'" />
                    </field>
                </xsl:for-each>
                <xsl:for-each select="dc:identifier[contains(., 'handle')][1]">
                    <field name="persistent_identifier_type">
                        <xsl:value-of select="'Handle'" />
                    </field>
                </xsl:for-each>
                <xsl:for-each select="dc:identifier[contains(., 'doi')][1]">
                    <field name="persistent_identifier_type">
                        <xsl:value-of select="'DOI'" />
                    </field>
                </xsl:for-each>
                <!-- A, data_access -->
                <!-- A, universe_included -->
                <!-- A, universe_excluded -->
                <!-- A, collection_mode -->
                <!-- A, time_method -->
                <!-- A, author -->
                <xsl:copy-of select="meta:getLangEnIfExists('author', dc:creator)" />
                <!-- A, author_affiliation -->
                <!-- A, keywords -->
                <xsl:if test="dc:subject[@xml:lang='en']">
                    <field name="keywords">
                        <xsl:value-of select="dc:subject[@xml:lang='en']" separator="; " />
                    </field>
                </xsl:if>
            </additional_fields>
        </entry>
    </xsl:template>

    <xsl:function name="meta:getLangEn">
        <xsl:param name="element" />
        <xsl:for-each select="$element">         
            <xsl:choose>
                <xsl:when test="@xml:lang='en'">
                    <xsl:value-of select="text()"/>
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
    </xsl:function>
    <xsl:function name="meta:getLangEnIfExists">
        <xsl:param name="fieldname" />
        <xsl:param name="element" />
        <xsl:for-each select="$element">         
            <xsl:choose>
                <xsl:when test="@xml:lang='en'">
                    <field name="{$fieldname}">
                        <xsl:value-of select="text()"/>
                    </field>
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
    </xsl:function>
</xsl:stylesheet>