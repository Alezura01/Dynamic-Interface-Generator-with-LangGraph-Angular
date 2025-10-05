import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService, FunctionDecision } from './app.service';
import { DynamicResponseComponent } from './dynamic-response/dynamic-response.component';
import { FormsModule } from '@angular/forms';
import { SharedDataService } from './shared-data.service';
import { Router } from '@angular/router';
import { RouterModule } from '@angular/router';
@Component({
  selector: 'app-root',
  imports: [RouterModule, FormsModule, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'prova_angular_now';

  public prompt: string = '';
  public response: any = null;
  public debug: boolean = false;
  isLoading: boolean = false;
  funzioneSelezionata?: FunctionDecision;

  constructor(
    private chatService: ChatService,
    private sharedDataService: SharedDataService,
    private router: Router
  ) { }
}
