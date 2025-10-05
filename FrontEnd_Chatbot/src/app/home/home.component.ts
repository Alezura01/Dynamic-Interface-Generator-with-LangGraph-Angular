import { Component,OnInit, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService, FunctionDecision } from '../app.service';
import { FormsModule } from '@angular/forms';
import { SharedDataService } from '../shared-data.service';
import { Router } from '@angular/router';
import { RouterModule } from '@angular/router';
import { ThemeService } from '../theme.service';
import { from } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterModule, FormsModule, CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
  encapsulation: ViewEncapsulation.None
})
export class HomeComponent implements OnInit{
  title = 'chatbot_ui';

  public prompt: string = '';
  public response: any = null;
  public messages: Array<Message> = [];
  public debug: boolean = false;
  isLoading: boolean = false;
  funzioneSelezionata?: FunctionDecision;

  constructor(
    private chatService: ChatService,
    private sharedDataService: SharedDataService,
    private router: Router,
    private themeService: ThemeService
  ) { }

  ngOnInit(): void {
    this.themeService.applyTheme();
    this.themeService.setBodyClass('root')
  }
  
  onSave2(){
    this.isLoading = true;
    this.messages.push(new Message('user', this.prompt, false, false));

    this.chatService.sendPrompt(this.prompt).subscribe({
      next: risposte => {

        const index = this.messages.findIndex(m => m.type === 'loading');
        if (index !== -1) this.messages.splice(index, 1);

        const allComponenti: string[] = [];
        const allContenuti: any[] = [];
        const allNomi: string[] = [];

        for (const risposta of risposte) {
          const nome = risposta.nome;
          const componente = risposta.componente;
          const contenuto = risposta;

          allNomi.push(nome);
          allComponenti.push(componente);
          allContenuti.push(contenuto);

        }

        const botMessage = new Message('bot', '', true, true, allNomi, allComponenti, allContenuti);
        this.messages.push(botMessage);

        this.sharedDataService.setData(allNomi, allComponenti, allContenuti);
        this.router.navigate(['/dynamic-response']);
        this.isLoading = false;
      }
    });
  }

  onClear(): void {
      this.messages = [];
  }

  onDebug(): void {
      this.debug = !this.debug;
    }

  data: any;
  }

export class Message {

  constructor(
    public type: string,
    public message: string,
    public debug: boolean,
    public isBot: boolean,
    public nome?: string[],
    public componente?: string[],
    public contenuto?: any[],
  ) {
    this.type = type.toUpperCase();
  }
}



