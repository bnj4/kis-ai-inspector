import { NextRequest, NextResponse } from 'next/server';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
type Context = { params: Promise<{path:string[]}> };
async function forward(req: NextRequest, ctx: Context) {
  const {path} = await ctx.params;
  const route = path.join('/');
  const allowed = req.method === 'GET' ? /^(health|providers|history(?:\/\d+)?|recommendations\/\d+)$/ : req.method === 'POST' ? /^analyze$/ : /^history\/\d+$/;
  if (!allowed.test(route)) return NextResponse.json({detail:'Ruta no disponible'}, {status:404});
  const base = process.env.BACKEND_URL || (process.env.RAILWAY_PROJECT_ID ? '' : 'http://127.0.0.1:8000');
  const token = process.env.INTERNAL_API_TOKEN || '';
  if (!base || (process.env.RAILWAY_PROJECT_ID && !token)) return NextResponse.json({detail:'Falta configurar la conexión privada con el backend.'},{status:503});
  try {
    const headers: Record<string,string> = {'Content-Type':'application/json'};
    if (token) headers['X-KIS-Internal-Token'] = token;
    let body: string | undefined;
    if (req.method === 'POST') {
      if (Number(req.headers.get('content-length') || 0) > 8192) return NextResponse.json({detail:'Solicitud demasiado grande.'},{status:413});
      body = await req.text();
      if (Buffer.byteLength(body) > 8192) return NextResponse.json({detail:'Solicitud demasiado grande.'},{status:413});
    }
    const res = await fetch(`${base.replace(/\/$/,'')}/api/${route}`,{method:req.method,headers,body,cache:'no-store',redirect:'error',signal:AbortSignal.timeout(240000)});
    return new NextResponse(res.body,{status:res.status,headers:{'Content-Type':res.headers.get('content-type') || 'application/json','Cache-Control':'no-store'}});
  } catch {
    return NextResponse.json({detail:'No se pudo conectar con el backend. Revisa BACKEND_URL y los registros de Railway.'},{status:502});
  }
}
export {forward as GET,forward as POST,forward as DELETE};
