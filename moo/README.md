
[LambdaMOO][] is a MUD server.  It is essentially a programmable chat
server.  That simplifies things a bit since one could write non-chat
networked applications on top of LambdaMOO.  "MOO" is just a shorthand
way to refer to LambdaMOO.

   - realms.jhc -- A module for JHCore which permits dividing up a MOO
     into several realms.   Each realm can have its own set of
     builders and realms limit where inter-realm connections may
     happen.   I made it for the educational MOO "Connections", but it
     should work on any JHCore-based MOO.
   - run-moo -- Script that runs the MOO process
   - moo.service -- systemd unit file that invokes run-moo.
   
I removed the old dbbackup/ directory as I haven't used any of those scripts in years. I currently use a little binary that watches the checkpoint destination and backups the DB to AWS S3 on update.

[LambdaMOO]: http://www.lambda.moo.mud.org/
