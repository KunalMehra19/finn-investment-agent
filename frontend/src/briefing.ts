import type {Dataset} from './types';
export function briefingStories(data:Dataset,mode:string,window:string){
 if(mode==='replay')return data.stories;
 const cutoff=Date.now()-(window==='7d'?7:1)*86400000;
 return (data.current_stories||[]).filter(s=>new Date(s.published).valueOf()>=cutoff&&new Date(s.published).valueOf()<=Date.now());
}
