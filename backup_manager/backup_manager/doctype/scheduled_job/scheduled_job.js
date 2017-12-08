// Copyright (c) 2017, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Scheduled Job', {
	refresh: function(frm) {

	},
	
	run_jobs:function(frm) {
		
		
		frappe.call({
			doc: frm.doc,
			method: "run_all_jobs",
			freeze: false,
			args: {
				freq: frm.doc.frequency,
			},
			callback: function(r) {
				
				if (r.exc)
				{
					
					frappe.msgprint(__("Job Complete"));
				}
			}
		}); 
	
	
			
		
		
			

	},
});
