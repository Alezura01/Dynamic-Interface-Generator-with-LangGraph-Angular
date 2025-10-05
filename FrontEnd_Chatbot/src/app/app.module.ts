import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { provideHttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { DynamicResponseComponent } from './dynamic-response/dynamic-response.component';

const routes: Routes = [
  { path: '', component: AppComponent }, // opzionale, per la home

  { path: 'dynamic-response', component: DynamicResponseComponent }
];

@NgModule({
  declarations: [AppComponent,
    DynamicResponseComponent

  ],
  imports: [
    BrowserModule,
    FormsModule,
    CommonModule,
    RouterModule.forRoot(routes)
  ],
  exports: [RouterModule],
  providers: [provideHttpClient()],
  schemas: [],
  bootstrap: [AppComponent]
})
export class AppModule {}

