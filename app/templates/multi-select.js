function genMultiSelect(id, selectableHeading, selectionHeading, cssCls) {
var filter = $('<input type="text" class="search-filter" autocomplete="off" placeholder="filter">')
filter.insertAfter("label[for=" + id + "]");
$("#" + id).multiSelect({
    keepOrder: true,
    selectableHeader: selectableHeading,
    selectionHeader: selectionHeading,
    cssClass: cssCls,
    selectableOptgroup: true,
    afterInit: function(ms){
        var searchString = '#' + this.$container.attr('id')+' .ms-elem-selectable:not(.ms-selected)'
        searchString += ', #' + this.$container.attr('id')+' .ms-elem-selection.ms-selected';
        this.filt = filter.quicksearch(searchString)
    },
    afterSelect: function(){
        this.filt.cache();
    },
    afterDeselect: function(){
        this.filt.cache();
    }
});
}