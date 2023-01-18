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
	
	
	
    if(doc.enable_backup){
		frappe.msgprint(__("Performing Backup"));
		frappe.call({
			method: "backup_manager.backup_manager.doctype.backup_manager.backup_manager.take_backup",
			freeze: true,
			callback:function (r) {
				//console.log(r)
			}
		})
		

		
    } else {
  	  frappe.msgprint(__("Backup is not enabled"));
    }
}
