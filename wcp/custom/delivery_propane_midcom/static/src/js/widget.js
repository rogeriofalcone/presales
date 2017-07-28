openerp.delivery_propane_midcom = function (instance) {
    var _t = instance.web._t,
    _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
//    instance.web.delivery_propane_midcom = instance.web.delivery_propane_midcom || {};


    instance.web.ListView.include({
        load_list: function(data){
                this._super(data);
                var self = this;
                if (this.model == 'delivery.propane'){
                        if (! this.$btn_delivery){
                                this.$btn_delivery = $(QWeb.render('ImportDelivery',{}));
                                $btn_delivery = $(QWeb.render('ImportDelivery',{}));
                                $btn_delivery.appendTo('.oe_list_buttons');
                                btn_date = this.$buttons.find('.btn_delivery')
                                        .click(function(){
                                        self.do_action({
                                        type: 'ir.actions.act_window',
                                        res_model: "delivery.load.midcom",
                                        views: [[false, 'form']],
                                        target: 'new',
                                        context: {},
                                    });
                                        });
                                btn_data_complete = this.$buttons.find('.btn_delivery_complete')
                                        .click(function(){
                                                tds = self.$('.oe_list_content tbody th input:checked');
                                        active_ids = _.map(tds, function(td){
                                                return $(td).closest('tr').data('id')
                                        });
                                        context = active_ids.length ? {'active_ids': active_ids, 'active_id': active_ids[0]} : {}
                                                self.do_action({
                                        type: 'ir.actions.act_window',
                                        res_model: "merge.picking",
                                        views: [[false, 'form']],
                                        target: 'new',
                                        context: context,
                                    });
                                        });
                        }

                }
        },
        import_delivery : function(){
//              alert("button called")


        }
    });

};
