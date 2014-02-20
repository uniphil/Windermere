SELECT
        node.nid as nid,
        node.vid as vid,
        node_revisions.title as title,
        node_revisions.body as body,
        node_revisions.timestamp as timestamp,
        files.filepath as filepath,
        files.filemime as mimetype,
        files.origname as original_name
    FROM node
        LEFT JOIN node_revisions
            ON node.vid = node_revisions.vid
        LEFT JOIN content_type_photo
            ON node.vid = content_type_photo.vid
        LEFT JOIN files
            ON content_type_photo.field_photo_fid = files.fid
    WHERE
        node.type = 'photo'
    -- LIMIT
    --     1 offset 40
