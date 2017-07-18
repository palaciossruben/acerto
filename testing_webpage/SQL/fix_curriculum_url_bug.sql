update users set curriculum_url = replace(curriculum_url, ' ', '_');
update users set curriculum_url = replace(curriculum_url, '(', '_');
update users set curriculum_url = replace(curriculum_url, ')', '_');
