SELECT
        node.nid AS nid,
        node.vid AS vid,
        node_revisions.title AS title,
        node_revisions.body AS body,
        node_revisions.timestamp AS timestamp,
        content_type_document.field_linkf_value AS path,
        content_type_document.field_type_filter_value AS type,
        content_type_document.field_author_value AS author,
        content_field_categories.field_categories_value as category
    FROM node
        LEFT JOIN node_revisions
            ON node.vid = node_revisions.vid
        LEFT JOIN content_type_document
            ON node.vid = content_type_document.vid
        LEFT JOIN content_field_categories
            ON node.vid = content_field_categories.vid
    WHERE
        node.type = 'document'
    -- LIMIT
    --     8 OFFSET 48
