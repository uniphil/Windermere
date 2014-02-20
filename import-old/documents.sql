SELECT
        node.nid AS nid,
        node.vid AS vid,
        node_revisions.title AS title,
        node_revisions.body AS body,
        node_revisions.timestamp AS timestamp,
        content_type_document.field_linkf_value AS path,
        content_type_document.field_type_filter_value AS type
    FROM node
        LEFT JOIN node_revisions
            ON node.vid = node_revisions.vid
        LEFT JOIN content_type_document
            ON node.vid = content_type_document.vid
    WHERE
        node.type = 'document'
    -- LIMIT
    --     1 OFFSET 40
