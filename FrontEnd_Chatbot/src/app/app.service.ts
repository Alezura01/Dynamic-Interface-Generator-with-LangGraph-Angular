import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';

export interface BotResponse {
  nome: string,
  componente: string;
  contenuto: {
    components?: any[];
    [key: string]: any;
  };
}

export interface FunctionDecision {
  function: string;
  args: { [key: string]: any};
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:2024/';

  constructor(private http: HttpClient) { }

  sendPrompt(input: string): Observable<BotResponse[]> {
  const body = { content: input };

  return this.http.post<any>(this.apiUrl, body).pipe(
    map(response => {

      let parsedResult = JSON.parse(response.result);

      return parsedResult.map((obj: any) => {
        const componente = obj.element;
        const nome = obj.name;

        const contenuto = { ...obj };
        delete contenuto.element;
        delete contenuto.name;

        return { componente, nome, contenuto };
      });
    })
  );
}

  sendAll(datiForm: any): Observable<BotResponse[]> {
    const body = { dati_form: datiForm };
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    return this.http.post<any>(this.apiUrl, body, { headers }).pipe(
      map(response => {
        const output = JSON.parse(response.result);
        const arr = Array.isArray(output) ? output : [output];
        return arr.map((item: any) => {
          const { element: componente, name: nome, ...rest } = item;
          return { componente, nome, contenuto: rest };
        });
      })
    );
  }
}

