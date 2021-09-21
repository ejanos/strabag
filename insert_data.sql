INSERT INTO public.pandasarchitect(
	architectname, createdate, modifydate, active)
	VALUES ('superadmin', '2021-09-16', '2021-09-16', true);

INSERT INTO public.users(
	firstname, lastname, email, password, createdat, active, confirmed, expireat)
	VALUES ('super', 'admin', 'email@email.com', 'sdfgsf', '2021-09-16', true, true, '2028-09-16');

INSERT INTO public.pandasproject(
	userid, pandasarchitectid, pandasprojectname)
	VALUES (1, 1, 'elso projekt');