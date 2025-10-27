#include "TCanvas.h" 
#include <sqlite3.h> 
#include "TGraph.h" 
#include <time.h> 
#include "TPaveText.h" 
#include "TLegend.h" 
#include "TH2.h" 
#include <stdio.h> 
#include "TMath.h"
#include <stdlib.h> 
#include <string.h>
#include "TString.h" 
#include <sys/stat.h>


int dpi = 72; 


void make_plot(int ngraphs, const char * title, const char ** columns, const char * table, const char * where,  sqlite3 * db) 
{
  TGraph ** gs = new TGraph* [ngraphs]; 

  TString str("select unixtime"); 
  for (int i = 0; i < ngraphs; i++) 
  {
    gs[i] = new TGraph(); 
    gs[i]->SetTitle(columns[i]); 
    gs[i]->SetLineColor(i+1); 
    gs[i]->SetMarkerColor(i+1); 
    str += ","; 
    str += columns[i]; 
  }

  str += " from "; 
  str += table ; 
  str +=" where " ; 
  str += where;
  str += ";"; 

  sqlite3_stmt * res; 
  const char * tail; 
  int err = sqlite3_prepare_v2(db, str.Data(), str.Length()+1, &res, &tail); 

  int ipt = 0; 

  double min_y = 1e99; 
  double max_y = -1e99; 
  while (sqlite3_step(res) == SQLITE_ROW)
  {
    double t= sqlite3_column_double(res,0); 
    for (int i = 0; i < ngraphs; i++)
    {
      double y = sqlite3_column_double(res,i+1); 
      if (y > max_y) max_y = y; 
      if (y < min_y) min_y = y; 
      gs[i]->SetPoint(ipt, t, y); 
    }
    ipt++; 
  }

  sqlite3_finalize(res); 

  if (ipt == 0) 
  {
    TPaveText * pt = new TPaveText(0.2,0.2,0.8,0.8); 
    pt->AddText("No results found"); 
    pt->AddText(str.Data()); 
    pt->Draw(); 
    return; 
  }

  TH2I axis("axis",title, 10, gs[0]->GetX()[0], gs[0]->GetX()[gs[0]->GetN()-1], 10, min_y-0.1*min_y, max_y+0.5*max_y); 
  axis.SetStats(false); 
  axis.GetXaxis()->SetTimeDisplay(1); 
  axis.GetXaxis()->SetLabelSize(2*axis.GetXaxis()->GetLabelSize());
  axis.GetYaxis()->SetLabelSize(2*axis.GetYaxis()->GetLabelSize());
  axis.DrawCopy(); 


  TLegend * leg = new TLegend(0.7,0.7,0.9,0.9); 
  for (int i = 0; i < ngraphs; i++) 
  {
    gs[i]->Draw("lpsame"); 
    char * renamed = strdup(columns[i]);
    char * c = strstr(renamed,"slave");
    if (c) memcpy(c,"auxbd", 5);
    c = strstr(renamed,"master");
    if (c) memcpy(c,"mainbd",6);

    leg->AddEntry(gs[i],TString::Format("%s (max: %g)", renamed, TMath::MaxElement(gs[i]->GetN(), gs[i]->GetY())), "lp"); 
    free(renamed);
  }
  leg->Draw(); 
}

static unsigned getFileSize(const char * file) 
{
  struct stat sb; 
  stat(file,&sb); 
  return sb.st_size; 
}

int main(int nargs, char ** args) 
{
  if (nargs < 3) 
  {
    fprintf(stderr,"Usage: %s output.pdf nsecs\n", args[0]); 
    return 1; 
  }

  char * outfile = args[1];
  int nsecs = atoi(args[2]); 

  TCanvas c("monitor","Monitor", 8.5*dpi,11*dpi); 
  c.Divide(1,3); 
  time_t t = time(0); 
  t -= nsecs; 

  TString where; 
  where.Form(" unixtime > %d ", t); 

  sqlite3 * db; 
  sqlite3_open(getenv("NUPHASE_SUM_DATABASE"),&db); 
  c.cd(1); 
  const char * columns1[4] = { "avg_rate","rate","max_rate", "min_rate" }; 
  make_plot(4, "Rates", columns1, "status_summary", where.Data(), db); 
  
 
  c.cd(2); 
  const char * columns2[3] = { "temp_master","temp_slave","temp_case" }; 
  make_plot(3, "Temperatures", columns2, "hk_summary", where.Data(), db); 
  
  c.cd(3); 
  const char * columns3[3] = { "current_master","current_slave","current_frontend" }; 
  make_plot(3, "Currents", columns3, "hk_summary", where.Data(), db); 

  sqlite3_close(db); 

  c.SaveAs(outfile); 
  while( getFileSize(outfile) > 50000)
  {
    /* Reduce size if too big */ 
    printf("too big (%d bytes), reducing window by 10 percent"); 
    c.SetWindowSize(0.9*c.GetWindowWidth(), 0.9 * c.GetWindowHeight()); 
    c.SaveAs(outfile); 
  }

  return 0; 
}
