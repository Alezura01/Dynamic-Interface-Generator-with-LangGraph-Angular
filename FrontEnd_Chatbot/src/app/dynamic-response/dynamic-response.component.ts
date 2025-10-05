import { Component, Output, EventEmitter, Input, OnInit } from '@angular/core';
import { MatTableComponent } from '../components/mat-table/mat-table.component';
import { MatInputComponent } from '../components/mat-input/mat-input.component';
import { ButtonComponent } from '../components/button/button.component';
import { MatListComponent } from '../components/mat-list/mat-list.component';
import { FormComponent } from '../components/form/form.component';
import { CommonModule } from '@angular/common';
import { ChatService } from '../app.service';
import { SharedDataService } from '../shared-data.service';
import { ThemeService } from '../theme.service';

@Component({
  selector: 'app-dynamic-response',
  imports: [CommonModule, MatTableComponent, FormComponent, MatInputComponent, ButtonComponent, MatListComponent],
  templateUrl: './dynamic-response.component.html',
  styleUrl: './dynamic-response.component.css'
})
export class DynamicResponseComponent implements OnInit {
  componenti: string[] = [];
  nomi: string[] = [];
  contenuti: any = '';
  isLoading: boolean = false;


  @Output() bottoneCliccato = new EventEmitter<string>();
  @Output() formInviato = new EventEmitter<void>();

  formData: { [key: string]: string | number } = {};

  constructor(
    private chatService: ChatService,
    private themeService: ThemeService,
    private sharedDataService: SharedDataService
  ) { }

  ngOnInit(): void {

    this.componenti = this.sharedDataService.getContenuti();
    this.nomi = this.sharedDataService.getComponenti();
    this.contenuti = this.sharedDataService.getNomi();

    this.themeService.applyTheme();
    this.themeService.setBodyClass('dynamic-response')
  }


  onBottoneClick(id: string) {
    this.isLoading = true;
    this.chatService.sendAll(this.formData).subscribe({
      next: res => {

        this.formInviato.emit();
        this.bottoneCliccato.emit();

        this.componenti = []
        this.nomi = []
        this.contenuti = []

        for (const item of res) {
          this.componenti.push(item.componente);
          this.contenuti.push(item);
          this.nomi.push(item.nome)
        }
        
        this.isLoading = false;
      }
    })
  }

  updateFormData(data: { [key: string]: string }) {
    this.formData = { ...this.formData, ...data };
  }

}
