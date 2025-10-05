import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SharedDataService {
  private nomi: string[] = []
  private componenti: string[] = [];
  private contenuti: any;

  setData(componenti: string[], contenuti: any, nomi:string[]) {
    this.nomi = nomi;
    this.componenti = componenti;
    this.contenuti = contenuti;
  }

  getNomi() : string[] {
    console.log(this.nomi)
    return this.nomi;
  }

  getComponenti(): string[] {
    console.log(this.componenti);
    return this.componenti;
  }

  getContenuti(): any {
    return this.contenuti;
  }

  clear() {
    this.componenti = [];
    this.contenuti = [];
    this.nomi = [];
  }

}
