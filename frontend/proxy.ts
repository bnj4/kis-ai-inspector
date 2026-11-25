import { NextRequest, NextResponse } from 'next/server';
import { createHash, timingSafeEqual } from 'node:crypto';
function equal(a:string,b:string) {
  return timingSafeEqual(createHash('sha256').update(a).digest(),createHash('sha256').update(b).digest());
}
export function proxy(req:NextRequest) {
  const username=process.env.APP_USERNAME || '';
  const password=process.env.APP_PASSWORD || '';
  if (!username || !password) {
    if (process.env.RAILWAY_PROJECT_ID || username || password) return new NextResponse('Configura APP_USERNAME y APP_PASSWORD en Railway.',{status:503});
    return NextResponse.next();
  }
  const auth=req.headers.get('authorization') || '';
  if (auth.startsWith('Basic ') && equal(Buffer.from(auth.slice(6),'base64').toString('utf8'),`${username}:${password}`)) return NextResponse.next();
  return new NextResponse('Acceso restringido a usuarios autorizados.',{status:401,headers:{'WWW-Authenticate':'Basic realm="KIS AI Inspector", charset="UTF-8"','Cache-Control':'no-store'}});
}
export const config = {matcher:['/((?!_next/static|_next/image|favicon.ico|healthz).*)']};
