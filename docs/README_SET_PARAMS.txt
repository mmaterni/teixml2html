=========================
file configurazione json
=========================
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type":"d",
  "before_id":"d"
}

html_params
    utilizza i par1ametri nei files html dopo la
    trasformazione da xml.
    il termine di sinnstra e la key quello di
    destra il valore da sosituire
        "text_nul""  => ""
        "<null>"    =>  "",
        "</null>"    =>  ""

html_tag_file
    file di configurazione csv per le entity html
    es. teimcfg/html.csv"

html_tag_type
    d = >  diplomatica
    i =>   interpretativa

before_id
    prefisso utilizzato per distinguere gli id
    dei file della diplmatica da quelli dell'interpretativa

=============================
flusso sostituzione parametri
=============================
write_html()
  parse_xml
  append_html_data()
      x_data=get_node_data()
      build_html_data(x_data)
        c_data=get_data_row_html_csv       
        
        x_items: le coppie key:value del nodo XML
        c_keys:  key degli items da prendere
        c_attrs: attrs in csv
        build_html_attrs(x_items, c_keys, c_attrs)
           return html_attrs
              x_items selzionati da c_keys c_attrs
           html_attrs = attrs2html(attrs)

           se in html_attrs esiste un parametro %...$
              replace_text_param(html_attrs, x_text)
              sostiuisce in html_attrs i %text% con x_data['text'] (preso da csv)

              sett_c_params(html_attrs, c_params)
              setta in html_attr i pametri %...%

              self.set_x_items(html_attrs, x_items)
              setta in html_attrs i parametri %...%

              remove_params_null(html_attrs)
              rimuove i parametri non settati

           se in c_text esiste un parametro %...$
              sett_c_params(c_text, c_params)
              set_x_items(c_text, x_items)
              # quando in c_data tetx=%%text%% il text di x_data
              # sostituisce %text$ . Es:
              # x_data x_text='c' ==>  in c_data c_text=%c$
              # se la sostituzione avviene viene posto x_text=''
              eplace_text_param(c_text, x_text)
              if is_replace:
                  x_text = ''
              sett_c_params(c_text, c_params)

            hb.opn(x_liv, h_tag, h_attrs, h_text, h_tail)
            oppure      
            hb.ovc(x_liv, h_tag, h_attrs, h_text, h_tail)

  set_overflow()
  check_html()
  set_html_params()
