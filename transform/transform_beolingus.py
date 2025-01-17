import re
from lxml import etree
from utils import input_output


def transform_in_tei(beo_as_dict):
    root = etree.Element('TEI', attrib={"xmlns": 'http://www.tei-c.org/ns/1.0'})

    ##HEADER
    header = etree.SubElement(root, 'teiHeader')

    fileDesc = etree.SubElement(header, 'fileDesc')
    titleStmt = etree.SubElement(fileDesc, 'titleStmt')
    title = etree.SubElement(titleStmt, 'title')
    title.text = 'TEI Version of Beolingus DE-EN'

    publicationStmt = etree.SubElement(fileDesc, 'publicationStmt')
    p_publicationStmt = etree.SubElement(publicationStmt, 'p')
    p_publicationStmt.text = 'Original Data: Copyright (c) :: Frank Richter <frank.richter.tu-chemnitz.de>'

    sourceDesc = etree.SubElement(fileDesc, 'sourceDesc')
    p_sourceDesc = etree.SubElement(sourceDesc, 'p')
    p_sourceDesc.text = 'Digi_Lex - TEI Version'

    ##TEXT
    text = etree.SubElement(root, 'text')
    body = etree.SubElement(text, 'body')

    usg_pattern = re.compile(r'(\[(.*?)\])')
    gramm_pattern = re.compile(r'(\{(.*?)\})')

    for k1, v1 in beo_as_dict.items():

        if len(v1) > 1:
            super_entry = etree.Element('superEntry')

        en_counter = 0
        for k2, v2 in v1.items():
            en_counter += 1

            entry = etree.Element('entry')

            splitted_forms = k2.split(';')
            splitted_senses = v2.split(';')

            for i, f in enumerate(splitted_forms):
                i += 1
                form = etree.SubElement(entry, 'form')
                form.attrib['{http://www.w3.org/XML/1998/namespace}id'] = "en_{}_f_{}_{}".format(str(k1), en_counter, i)

                orth = etree.SubElement(form, 'orth')
                orth.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "de"

                gramm_matches = gramm_pattern.findall(f)
                usg_matches = usg_pattern.findall(f)

                # we assume , and only allow one gram per form
                if len(gramm_matches) > 0:
                    grammGrp = etree.SubElement(form, 'gramGrp')
                    gramm = etree.SubElement(grammGrp, 'gram')
                    gramm.text = gramm_matches[0][1]
                    f = f.replace(gramm_matches[0][0], '')

                if len(usg_matches) > 0:
                    for match in usg_matches:
                        usg = etree.SubElement(form, 'usg')
                        usg.text = match[1]
                        f = f.replace(match[0], '')

                # f = input_output.clean_up_str(f)
                orth.text = f.strip()
            for i, s in enumerate(splitted_senses):
                i += 1

                sense = etree.SubElement(entry, 'sense')
                sense.attrib['{http://www.w3.org/XML/1998/namespace}id'] = "en_{}_s_{}_{}".format(str(k1), en_counter,
                                                                                                  i)
                sense.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"

                usg_matches = usg_pattern.findall(s)

                definition = etree.SubElement(sense, 'def')

                if len(usg_matches) > 0:
                    for match in usg_matches:
                        usg = etree.SubElement(sense, 'usg')
                        usg.text = match[1]
                        s = s.replace(match[0], '')
                # s = input_output.clean_up_str(s)
                definition.text = s.strip()

            if len(v1) > 1:
                entry.attrib['{http://www.w3.org/XML/1998/namespace}id'] = "en_{}_{}".format(str(k1), en_counter)
                super_entry.append(entry)
                super_entry.attrib['{http://www.w3.org/XML/1998/namespace}id'] = "en_{}".format(str(k1))

                body.append(super_entry)

            else:
                entry.attrib['{http://www.w3.org/XML/1998/namespace}id'] = "en_{}".format(str(k1))

                body.append(entry)

    et = etree.ElementTree(root)
    return et

def validate(tei_file, rng_schema):
    parser = etree.XMLParser(recover=True)
    tei_parsed = etree.parse(tei_file, parser)
    rng_parsed = etree.parse(rng_schema)
    rng_validator = etree.RelaxNG(rng_parsed)
    validation_rng = rng_validator.validate(tei_parsed)
    return validation_rng

et = transform_in_tei(input_output.deserialize('data_to_process/splitted_beolingus_prepro.pickle'))
et.write('data_to_publish/beo_en_de.tei', pretty_print=True, xml_declaration=True, encoding='utf-8')
