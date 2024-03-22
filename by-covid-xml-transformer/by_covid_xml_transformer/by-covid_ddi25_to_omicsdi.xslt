<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:xml="http://www.w3.org/XML/1998/namespace"
xmlns:meta="transformation:metadata"
xmlns:c="ddi:codebook:2_5"
xmlns:ddi="http://www.ddialliance.org/Specification/DDI-Codebook/2.5/XMLSchema/codebook.xsd"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
version="2.0"
exclude-result-prefixes="#all">

    <meta:metadata>
        <identifier>ddi-2.5-to-omicsdi</identifier>
        <title>DDI 2.5 to OmicsDI</title>
        <description>Convert DDI Codebook (2.5) to OmicsDI format</description>
        <outputFormat>XML</outputFormat>
        <parameters>
            <parameter name="entry_id" format="xs:string" description="Unique entry id for each dataset metadata"/>
        </parameters>
    </meta:metadata>

    <xsl:param name="entry_id">{$entry_id}</xsl:param>

    <xsl:output indent="yes" omit-xml-declaration="yes" />

    <xsl:template match="c:codeBook">
        <entry id="{$entry_id}">
            <!-- M, name -->
            <name>
                <xsl:choose>
                    <xsl:when test="c:stdyDscr/c:citation/c:titlStmt/c:titl and c:stdyDscr/c:citation/c:titlStmt/c:titl[@xml:lang='en']">
                        <xsl:copy-of select="meta:getLangEn(c:stdyDscr/c:citation/c:titlStmt/c:titl)" />
                    </xsl:when>
                    <xsl:when test="c:stdyDscr/c:citation/c:titlStmt/c:parTitl and c:stdyDscr/c:citation/c:titlStmt/c:parTitl[@xml:lang='en']">
                        <xsl:copy-of select="meta:getLangEn(c:stdyDscr/c:citation/c:titlStmt/c:parTitl)" />
                    </xsl:when>
                </xsl:choose>
            </name>
            <!-- M, description -->
            <description>
                <xsl:copy-of select="meta:getLangEn(c:stdyDscr/c:stdyInfo/c:abstract)" />
            </description>
            <dates>
                <!-- M, publication -->
                <date>
                    <xsl:attribute name="type">publication</xsl:attribute>
                    <xsl:attribute name="value">
                        <xsl:choose>
                            <xsl:when test="c:stdyDscr/c:citation/c:distStmt/c:distDate[@xml:lang='en'][@date]">
                                <xsl:value-of select="c:stdyDscr/c:citation/c:distStmt/c:distDate[@xml:lang='en']/@date"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="c:stdyDscr/c:citation/c:distStmt/c:distDate/@date"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </date>
                <!-- M, updated -->
                <date>
                    <xsl:attribute name="type">updated</xsl:attribute>
                    <xsl:attribute name="value">
                        <xsl:choose>
                            <xsl:when test="c:stdyDscr/c:citation/c:verStmt/c:version[@xml:lang='en'][@date]">
                                <xsl:value-of select="c:stdyDscr/c:citation/c:verStmt/c:version[@xml:lang='en']/@date"/>
                            </xsl:when>
                            <xsl:when test="c:stdyDscr/c:citation/c:verStmt/c:version[@date]">
                                <xsl:value-of select="c:stdyDscr/c:citation/c:verStmt/c:version/@date"/>
                            </xsl:when>
                            <xsl:when test="c:stdyDscr/c:citation/c:distStmt/c:distDate[@xml:lang='en'][@date]">
                                <xsl:value-of select="c:stdyDscr/c:citation/c:distStmt/c:distDate[@xml:lang='en']/@date"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="c:stdyDscr/c:citation/c:distStmt/c:distDate/@date"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </date>
                <!-- A, collection_single_date -->
                <xsl:choose>
                    <xsl:when test="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='single'][@xml:lang='en'][@date]">
                        <date type='collection_single_date'>
                            <xsl:attribute name="value">
                                <xsl:value-of select="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='single'][@xml:lang='en']/@date"/>
                            </xsl:attribute>
                        </date>
                    </xsl:when>
                    <xsl:when test="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='single'][@date]">
                        <date type='collection_single_date'>
                            <xsl:attribute name="value">
                                <xsl:value-of select="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='single']/@date"/>
                            </xsl:attribute>
                        </date>
                    </xsl:when>
                </xsl:choose>
                <!-- A, collection_start_date -->
                <xsl:choose>
                    <xsl:when test="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='start'][@xml:lang='en'][@date]">
                        <date type='collection_start_date'>
                            <xsl:attribute name="value">
                                <xsl:value-of select="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='start'][@xml:lang='en']/@date"/>
                            </xsl:attribute>
                        </date>
                    </xsl:when>
                    <xsl:when test="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='start'][@date]">
                        <date type='collection_start_date'>
                            <xsl:attribute name="value">
                                <xsl:value-of select="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='start']/@date"/>
                            </xsl:attribute>
                        </date>
                    </xsl:when>
                </xsl:choose>
                <!-- A, collection_end_date -->
                <xsl:choose>
                    <xsl:when test="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='end'][@xml:lang='en'][@date]">
                        <date type='collection_end_date'>
                            <xsl:attribute name="value">
                                <xsl:value-of select="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='end'][@xml:lang='en']/@date"/>
                            </xsl:attribute>
                        </date>
                    </xsl:when>
                    <xsl:when test="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='end'][@date]">
                        <date type='collection_end_date'>
                            <xsl:attribute name="value">
                                <xsl:value-of select="c:stdyDscr/c:stdyInfo/c:sumDscr/c:collDate[@event='end']/@date"/>
                            </xsl:attribute>
                        </date>
                    </xsl:when>
                </xsl:choose>
            </dates>
            <additional_fields>
                <!-- M, full_dataset_link -->
                <field name="full_dataset_link">
                    <xsl:copy-of select="meta:getLangEnByAttribute(c:stdyDscr/c:citation/c:holdings, 'URI')" />
                </field>
                <!-- M, repository -->
                <field name="repository">
                    <xsl:copy-of select="meta:getLangEn(c:stdyDscr/c:citation/c:distStmt/c:distrbtr)" />
                </field>
                <!-- A, sample_protocol -->
                <xsl:copy-of select="meta:getLangEnIfExists('sample_protocol', c:stdyDscr/c:method/c:dataColl/c:sampProc)" />
                <!-- A, analysis_unit -->
                <xsl:copy-of select="meta:getLangEnIfExists('analysis_unit', c:stdyDscr/c:stdyInfo/c:sumDscr/c:anlyUnit)" />
                <!-- A, spatial_coverage -->
                <xsl:copy-of select="meta:getLangEnIfExists('spatial_coverage', c:stdyDscr/c:stdyInfo/c:sumDscr/c:nation)" />
                <!-- A, temporal_coverage -->
                <!-- A, persistent_identifier -->
                <xsl:if test="c:stdyDscr/c:citation/c:titlStmt/c:IDNo">
                    <field name="persistent_identifier">
                        <xsl:for-each select="c:stdyDscr/c:citation/c:titlStmt/c:IDNo">
                            <xsl:choose>
                                <xsl:when test="@xml:lang='en'">
                                    <xsl:choose>
                                        <!-- @agency should only contain values from https://vocabularies.cessda.eu/vocabulary/CessdaPersistentIdentifierTypes?lang=en
                                             but currently (July 2022) it sometimes also has values such as datacite (which means DOI) -->
                                        <xsl:when test="@agency='ARK' or @agency='DOI' or @agency='Handle' or @agency='URN' or @agency='datacite'">
                                            <xsl:value-of select="text()" />
                                        </xsl:when>
                                    </xsl:choose>
                                </xsl:when>
                            </xsl:choose>
                        </xsl:for-each>
                    </field>
                </xsl:if>
                <!-- A, persistent_identifier_type -->
                <xsl:if test="c:stdyDscr/c:citation/c:titlStmt/c:IDNo">
                    <field name="persistent_identifier_type">
                        <xsl:for-each select="c:stdyDscr/c:citation/c:titlStmt/c:IDNo">
                            <xsl:choose>
                                <xsl:when test="@xml:lang='en'">
                                    <xsl:choose>
                                        <!-- @agency should only contain values from https://vocabularies.cessda.eu/vocabulary/CessdaPersistentIdentifierTypes?lang=en
                                             but currently (July 2022) it sometimes also has values such as datacite (which means DOI) -->
                                        <xsl:when test="@agency='ARK' or @agency='DOI' or @agency='Handle' or @agency = 'URN'">
                                            <xsl:value-of select="@agency" />
                                        </xsl:when>
                                        <xsl:when test="@agency='datacite'">
                                            <xsl:value-of select="'DOI'" />
                                        </xsl:when>
                                    </xsl:choose>
                                </xsl:when>
                            </xsl:choose>
                        </xsl:for-each>
                    </field>
                </xsl:if>
                <!-- A, data_access -->
                <xsl:copy-of select="meta:getLangEnIfExists('data_access', c:stdyDscr/c:dataAccs/c:useStmt/c:restrctn)" />
                <!-- A, universe_included -->
                <!-- A, universe_excluded -->
                <xsl:for-each select="c:stdyDscr/c:stdyInfo/c:sumDscr/c:universe">
                    <xsl:choose>
                        <xsl:when test="@xml:lang='en' and @clusion='I'">
                            <field name="universe_included">
                                <xsl:value-of select="text()" />
                            </field>
                        </xsl:when>
                        <xsl:when test="@xml:lang='en' and @clusion='E'">
                            <field name="universe_excluded">
                                <xsl:value-of select="text()" />
                            </field>
                        </xsl:when>
                    </xsl:choose>
                </xsl:for-each>
                <!-- A, collection_mode -->
                <xsl:copy-of select="meta:getLangEnIfExists('collection_mode', c:stdyDscr/c:method/c:dataColl/c:collMode)" />
                <!-- A, time_method -->
                <xsl:copy-of select="meta:getLangEnIfExists('time_method', c:stdyDscr/c:method/c:dataColl/c:timeMeth)" />
                <!-- A, author -->
                <!-- A, author_affiliation -->
                <xsl:for-each select="c:stdyDscr/c:citation/c:rspStmt/c:AuthEnty">
                    <xsl:choose>
                        <xsl:when test="@xml:lang='en'">
                            <field name="author">
                                <xsl:value-of select="text()" />
                            </field>
                            <xsl:choose>
                                <xsl:when test="@affiliation">
                                    <field name="author_affiliation">
                                        <xsl:value-of select="@affiliation" />
                                    </field>
                                </xsl:when>
                            </xsl:choose>
                        </xsl:when>
                    </xsl:choose>
                </xsl:for-each>
                <!-- A, keywords -->
                <xsl:if test="c:stdyDscr/c:stdyInfo/c:subject/c:keyword[@xml:lang='en']">
                    <field name="keywords">
                        <xsl:value-of select="c:stdyDscr/c:stdyInfo/c:subject/c:keyword[@xml:lang='en']" separator="; " />
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
    <xsl:function name="meta:getLangEnByAttribute">
        <xsl:param name="element" />
        <xsl:param name="attribute" />
        <xsl:for-each select="$element">         
            <xsl:choose>
                <xsl:when test="@xml:lang='en'">
                    <xsl:value-of select="@*[name() = $attribute]" />
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
    </xsl:function>
</xsl:stylesheet>