$.extend(cur_frm.cscript, {
	onload_post_render: function() {
		cur_frm.fields_dict.manual_backup.$input.addClass("btn-primary");
	},
	
	validate_send_notifications_to: function() {
		if(!cur_frm.doc.send_notifications_to) {
			msgprint(__("Please specify") + ": " +
				__(frappe.meta.get_label(cur_frm.doctype,
					"send_notifications_to")));
			return false;
		}

		return true;
	}

});


cur_frm.cscript.manual_backup = function(doc,cdt,cdn){
	msgprint(__("Performing Backup"));
	
	
    if(doc.enable_backup){
		var callback = function(r, rt){
			if (r.message)
			{
				msgprint(__("Backup Complete"));

			}
		}

		return $c('runserverobj', args={'method':'take_backupsmethod','docs':doc},callback);
		

		
    } else {
  	  msgprint(__("Backup is not enabled"));
    }
}
