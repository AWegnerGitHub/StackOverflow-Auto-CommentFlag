select top 16000
  c.id as [Comment Link], 
  c.text, 
  c.id,
  c.score as 'CommentScore',
  c.userid,
  u.reputation,
  p.posttypeid,
  c.creationdate,
  '1' as 'Flag Type'
from 
  comments c,
  users u,
  posts p

where c.creationdate > {ts '2014-04-01 00:00:00'}
and c.creationdate < {ts '2014-05-18 23:59:59'}
and (c.score is null or c.score = 0)
and (text not like '%mark%answer%' 
  and text not like '%mark%accept%' 
  and text not like '%accept%answer%'
  and text not like '%lease%accept%'
  and text not like '%mark%answer%'
  and text not like '%thank%you%'
  and text not like '%.....'
  and text not like '%thx%you%'
  and text not like 'thank%'
  and text not like 'Thank%'
  and text not like '%+1%'
  )
and len(text) < 100
and c.userid = u.id
and c.postid = p.id
order by c.creationdate desc