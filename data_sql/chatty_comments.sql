select 
  c.id as [Comment Link], 
  c.text, 
  c.id,
  c.score as 'CommentScore',
  c.userid,
  u.reputation,
  p.posttypeid,
  c.creationdate,
  '5' as 'Flag Type'
from 
  comments c,
  users u,
  posts p

where c.creationdate > {ts '2014-04-01 00:00:00'}
and (c.score is null or c.score = 0)
and (text like '%mark%answer%' 
  or text like '%mark%accept%' 
  or text like '%accept%answer%'
  or text like '%lease%accept%'
  or text like '%mark%answer%'
  or text like '%thank%you%'
  or text like '%.....'
  or text like '%thx%you%'
  )
and len(text) < 100
and c.userid = u.id
and c.postid = p.id
order by c.creationdate desc