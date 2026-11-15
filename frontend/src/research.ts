import type {Dataset,Answer} from './types';
export function retrieve(data:Dataset,ticker:string,question:string):Answer {
  const all=data.insights[ticker]||[];
  if(!all.length)return {conclusion:'Document research unavailable for this ticker.',insights:[],unknowns:['The market snapshot may be available, but no primary documents are indexed for this company. Try a company in the deep research collection.'],engine:'Indexed evidence',status:'partial'};
  const tokens=question.toLowerCase().match(/[a-z]{3,}/g)||[];
  const stop=new Set(['the','what','does','this','that','have','with','from','company','tell','about','changed']);
  const ranked=all.map(i=>({i,score:tokens.filter(t=>!stop.has(t)&&`${i.tags} ${i.title} ${i.text}`.toLowerCase().includes(t)).length})).sort((a,b)=>b.score-a.score);
  if(!ranked[0]?.score)return {conclusion:'This question is not answered by the indexed evidence.',insights:[],unknowns:['Try asking about revenue, margins, business drivers or management guidance. FINN will not fill evidence gaps with a guess.'],engine:'Indexed evidence',status:'partial'};
  const selected=ranked.filter(r=>r.score>0).slice(0,3).map(r=>r.i);
  return {conclusion:selected[0].title+'.',insights:selected,unknowns:['This answer covers the dated documents cited below. It does not establish the latest company position or provide an investment recommendation.'],engine:'Indexed evidence · no AI synthesis',status:'verified'};
}
