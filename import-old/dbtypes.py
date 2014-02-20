from collections import namedtuple

# node                     pk
Node = namedtuple('Node', 'nid vid type language title uid status created changed comment promote moderate sticky tnid translate')
# node_revisions                               pk
NodeRevision = namedtuple('NodeRevision', 'nid vid uid title body teaser log timestamp format')
# content_type_document            pk
Document = namedtuple('Document', 'vid nid field_document_type_value field_author_value field_linkf_value field_type_filter_value')



# content_field_categories         pk      pk
Category = namedtuple('Category', 'vid nid delta field_categories_value')

# files                    pk
File = namedtuple('File', 'fid uid filename filepath filemime filesize status timestamp origname')


# content_type_photo         pk
Photo = namedtuple('Photo', 'vid nid field_photo_fid field_photo_list field_photo_data field_shot_value field_weight_value')


# term_data                        pk
TermData = namedtuple('TermData', 'tid vid name description weight')
# term_node                            pk  pk
TermNode = namedtuple('TermNode', 'nid vid tid')



# content_field_date       pk
Date = namedtuple('Date', 'vid nid field_date_value')

# node_type                        pk
NodeType = namedtuple('NodeType', 'type name module description help has_title title_label has_body body_label min_word_count custom modified locked orig_type')


# filefield_paths  no pk???
FilePath = namedtuple('FilePath', 'type field filename filepath')
# content_field_partners         pk      pk
Partner = namedtuple('Partner', 'vid nid delta field_partners_fid field_partners_list field_partners_data')
# content_node_field    pk
NodeField = namedtuple('NodeField', 'field_name type global_settings required multiple db_storage module db_columns active locked')
# content_node_field_instance                pk         pk
NodeFieldInstance = namedtuple('NodeField', 'field_name type_name weight label widget_type widget_settings display_settings description widget_module widget_active')
# content_type_page        pk
Page = namedtuple('Page', 'vid nid')
# content_type_personnel             pk
Personnel = namedtuple('Personnel', 'vid nid')
# location                         pk
Location = namedtuple('Location', 'lid name street additional city province postal_code country latitude longitude source is_primary')
# locaiton_instance  no pk???
LocationInstance = namedtuple('LocationInstance', 'nid vid uid genid lid')
# upload                       pk      pk
Upload = namedtuple('Upload', 'fid nid vid description list weight')
# term_relation                            pk
TermRelation = namedtuple('TermRelation', 'trid tid1 tid2')
# term_hierarchy                             pk  pk
TermHierarchy = namedtuple('TermHierarchy', 'tid parent')
